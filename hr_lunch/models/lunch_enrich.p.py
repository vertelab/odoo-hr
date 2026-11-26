"""Address enrichment for the lunch catalogue.

Two sources, tried in order:

1. Visit Linköping (visitlinkoping.se). The site publishes a restaurant index
   and one detail page per restaurant, and the detail page carries the street
   address and the map marker's coordinates. This is the better source: the
   address is written for visitors, not derived from a map node.
2. Nominatim (OpenStreetMap), as a fallback for names Visit Linköping does not
   list. A Nominatim hit on a restaurant node gives coordinates, not a street
   address; the address is then read back with a reverse lookup on the same
   service.

The policy is `fill_empty`: a field is written only when it is empty. A manual
address is never replaced, and a second run over the same data does nothing.
That is the whole of what makes it safe to run again.

The parsing functions are plain functions with no Odoo imports, so they can be
tested against saved HTML without a database.
"""

import html
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from odoo import _, api, models

from .res_config_settings import NOMINATIM_USER_AGENT

_logger = logging.getLogger(__name__)

# Nominatim's policy is a rate, not a per-record rule: at most one request per
# second across the whole run. A module-level timestamp survives the recordset
# the loop iterates over -- an attribute on `self` does not, because a
# recordset does not accept attribute assignment.
_nominatim_last_call = 0.0

# Same User-Agent for every external call. OpenStreetMap's usage policy
# requires a real one, and it is good manners towards the other services too.
# The literal is repeated here, rather than only imported, so that a grep for
# the bot name finds every module that calls out.
USER_AGENT = "VertelLunchBot/1.0 (info@vertel.se)"
assert USER_AGENT == NOMINATIM_USER_AGENT, "User-Agent must match the settings module"

VISITLINKOPING_BASE = "https://visitlinkoping.se"
# The site's own search index, the one its autocomplete reads. It lists every
# page with its title and slug, which is what we need to find a restaurant.
VISITLINKOPING_INDEX_URL = (
    VISITLINKOPING_BASE + "/wp-content/uploads/theme_cache/autocomplete-se.json"
)
# Every restaurant page lives under this prefix. The index entry carries the
# slug with the prefix glued to the title, so the prefix is also the marker
# that tells a restaurant page from a hotel or a campsite.
VISITLINKOPING_SECTION = "ata-dricka"

VISITLINKOPING_TIMEOUT = 10
NOMINATIM_TIMEOUT = 10
# Nominatim's usage policy: at most one request per second. Enforced between
# every Nominatim call, not only between records.
NOMINATIM_MIN_INTERVAL = 1.0

# A Swedish postal code written as "582 49" or "58249".
POSTCODE_RE = re.compile(r"\b\d{3}\s?\d{2}\b")
# A house number is a digit run, optionally followed by one letter ("43J").
HOUSE_NUMBER_RE = re.compile(r"\b\d+[A-Za-z]?\b")
# The map marker on a Visit Linköping detail page. The page also contains a
# second lat/lng pair for the site's own map widget; that one is not the
# restaurant, so the marker class is part of the match.
VISITLINKOPING_MARKER_RE = re.compile(
    r'class="google-marker-c"\s+lat="(-?\d+(?:\.\d+)?)"\s+lng="(-?\d+(?:\.\d+)?)"'
)
# The address line in the detail page's contact block.
VISITLINKOPING_ADDRESS_RE = re.compile(
    r'list-item--address">(.*?)</li>', re.S
)
VISITLINKOPING_TITLE_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
# The slug in an index entry: the section prefix, the slug, then a space or the
# end of the string. The entry text is title + description + the glued slug.
VISITLINKOPING_SLUG_RE = re.compile(
    re.escape(VISITLINKOPING_SECTION) + r"([a-z0-9-]+?)(?:\s|$)"
)
TAG_RE = re.compile(r"<[^>]+>")


# ----------------------------------------------------------------------
# Parsing — plain functions, no Odoo imports
# ----------------------------------------------------------------------
def normalize_name(name):
    """Lowercase, strip tags and punctuation, for comparing two names.

    "Grekiska Grill &amp; Bar" and "Grekiska Grill & Bar" are the same
    restaurant. So are "O'Learys" and "OLearys".
    """
    if not name:
        return ""
    text = html.unescape(name)
    text = TAG_RE.sub("", text)
    return re.sub(r"[^0-9a-zåäö]", "", text.lower())


def split_street(address):
    """Split a Swedish address line into (street, postal code).

    "Johannesborgparken 1A, 582 49 Linköping" -> ("Johannesborgparken 1A",
    "582 49"). The city is dropped: the catalogue is Linköping, and a city name
    in the field only makes the list harder to read.

    Returns (None, None) when no postal code is found. A line without a postal
    code is not an address we can trust, and the caller counts it as uncertain
    rather than writing half of it.
    """
    if not address:
        return None, None
    text = " ".join(html.unescape(TAG_RE.sub("", address)).split())
    match = POSTCODE_RE.search(text)
    if not match:
        return None, None
    postcode = " ".join(match.group(0).split())
    street = text[: match.start()].strip(" ,")
    if not street:
        return None, None
    return street, postcode


def parse_visitlinkoping_page(page):
    """Address and coordinates from a Visit Linköping detail page.

    Returns {"address", "street", "postcode", "lat", "lon", "title"}. Missing
    pieces are None; the caller decides what a partial result is worth.
    """
    result = {"address": None, "street": None, "postcode": None,
              "lat": None, "lon": None, "title": None}

    title = VISITLINKOPING_TITLE_RE.search(page or "")
    if title:
        result["title"] = " ".join(html.unescape(TAG_RE.sub("", title.group(1))).split())

    marker = VISITLINKOPING_MARKER_RE.search(page or "")
    if marker:
        result["lat"] = float(marker.group(1))
        result["lon"] = float(marker.group(2))

    address = VISITLINKOPING_ADDRESS_RE.search(page or "")
    if address:
        result["address"] = " ".join(html.unescape(address.group(1)).split())
        result["street"], result["postcode"] = split_street(result["address"])

    return result


def parse_visitlinkoping_index(payload):
    """[{name, slug}] for every restaurant page in the site's search index.

    The index is a JSON object whose "data" is a list of rows. Each row is
    [id, title, text, url, ...] and, for a restaurant page, the text ends with
    "ata-dricka<slug>". Rows without that marker are hotels, campsites or
    articles and are skipped.
    """
    try:
        rows = json.loads(payload)["data"]
    except (ValueError, KeyError, TypeError):
        _logger.warning("Visit Linköping index is not the expected JSON")
        return []

    entries = []
    seen = set()
    for row in rows:
        try:
            title, text = row[1], row[2]
        except (IndexError, TypeError):
            continue
        match = VISITLINKOPING_SLUG_RE.search(text or "")
        if not match:
            continue
        slug = match.group(1)
        if slug in seen:
            continue
        seen.add(slug)
        entries.append({"name": html.unescape(title or ""), "slug": slug})
    return entries


def find_index_entry(entries, name):
    """The index entry whose title matches `name`, or None.

    Exact match on the normalized title only. A partial match would put one
    restaurant's address on another's row, which is worse than no address.
    """
    wanted = normalize_name(name)
    if not wanted:
        return None
    for entry in entries:
        if normalize_name(entry["name"]) == wanted:
            return entry
    return None


def parse_nominatim_address(payload):
    """Street address from a Nominatim reverse response.

    Returns (street, postcode) or (None, None). The house number is kept when
    Nominatim has one; without it the address is a street, which is still
    better than an empty field but is reported as uncertain by the caller.
    """
    try:
        address = json.loads(payload).get("address") or {}
    except (ValueError, AttributeError):
        return None, None
    road = address.get("road")
    if not road:
        return None, None
    house_number = address.get("house_number")
    street = f"{road} {house_number}" if house_number else road
    return street, address.get("postcode")


def is_house_number_address(street):
    """True when the address line carries a house number.

    A street without a number is a street-level hit: right block, wrong door.
    The spec calls that uncertain, and it is written anyway — it is better than
    nothing — but it is counted separately.
    """
    return bool(street and HOUSE_NUMBER_RE.search(street))


# ----------------------------------------------------------------------
# The action
# ----------------------------------------------------------------------
class LunchChoice(models.Model):
    _inherit = "lunch.choice"

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------
    @api.model
    def _enrich_fetch(self, url, timeout):
        """GET `url` and return the body as text, or None on any failure.

        A source that is down is a normal outcome. It must not stop the run:
        the next record is tried, and the report counts what was not found.
        """
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as error:
            # 404 is the expected answer for a slug that does not exist.
            _logger.info("Enrichment: %s answered %s", url, error.code)
        except Exception as error:  # network, timeout, TLS, bad encoding
            _logger.warning("Enrichment: could not fetch %s: %s", url, error)
        return None

    # ------------------------------------------------------------------
    # Source 1 — Visit Linköping
    # ------------------------------------------------------------------
    @api.model
    def _enrich_index(self):
        """The site's restaurant index, fetched once per run.

        One request for the whole run instead of one per restaurant. An empty
        list means the source is unavailable, and every record falls through
        to Nominatim.
        """
        payload = self._enrich_fetch(VISITLINKOPING_INDEX_URL, VISITLINKOPING_TIMEOUT)
        if not payload:
            return []
        entries = parse_visitlinkoping_index(payload)
        _logger.info("Enrichment: Visit Linköping index has %s restaurants", len(entries))
        return entries

    @api.model
    def _enrich_from_visitlinkoping(self, name, entries):
        """Look `name` up on Visit Linköping.

        Returns the parsed page, or None when the restaurant is not listed or
        the page carries neither an address nor a position.
        """
        entry = find_index_entry(entries, name)
        if not entry:
            return None
        url = f"{VISITLINKOPING_BASE}/{VISITLINKOPING_SECTION}/{entry['slug']}/"
        page = self._enrich_fetch(url, VISITLINKOPING_TIMEOUT)
        if not page:
            return None
        parsed = parse_visitlinkoping_page(page)
        if not parsed["street"] and parsed["lat"] is None:
            return None
        parsed["source"] = "visitlinkoping"
        parsed["url"] = url
        return parsed

    # ------------------------------------------------------------------
    # Source 2 — Nominatim
    # ------------------------------------------------------------------
    @api.model
    def _enrich_nominatim_throttle(self):
        """Keep at least NOMINATIM_MIN_INTERVAL between Nominatim calls.

        The interval is tracked on the model instance, which lives for the
        duration of the run. Their policy is a rate, not a per-record rule.
        """
        global _nominatim_last_call
        wait = NOMINATIM_MIN_INTERVAL - (time.monotonic() - _nominatim_last_call)
        if wait > 0:
            time.sleep(wait)
        _nominatim_last_call = time.monotonic()

    @api.model
    def _enrich_from_nominatim(self, name):
        """Search Nominatim for `name, Linköping` and read the address back.

        The search gives the position. The address comes from a reverse lookup
        on that position, because a Nominatim search result is a map node and
        its display name is a list of administrative areas, not an address.
        """
        query = urllib.parse.urlencode(
            {"q": f"{name}, Linköping", "format": "json", "limit": 1}
        )
        self._enrich_nominatim_throttle()
        payload = self._enrich_fetch(
            f"https://nominatim.openstreetmap.org/search?{query}", NOMINATIM_TIMEOUT
        )
        if not payload:
            return None
        try:
            results = json.loads(payload)
        except ValueError:
            return None
        if not results:
            return None

        hit = results[0]
        try:
            lat, lon = float(hit["lat"]), float(hit["lon"])
        except (KeyError, TypeError, ValueError):
            return None

        parsed = {"address": None, "street": None, "postcode": None,
                  "lat": lat, "lon": lon, "source": "nominatim", "url": None}

        reverse_query = urllib.parse.urlencode(
            {"lat": lat, "lon": lon, "format": "json", "zoom": 18}
        )
        self._enrich_nominatim_throttle()
        reverse = self._enrich_fetch(
            f"https://nominatim.openstreetmap.org/reverse?{reverse_query}",
            NOMINATIM_TIMEOUT,
        )
        if reverse:
            street, postcode = parse_nominatim_address(reverse)
            if street:
                parsed["street"] = street
                parsed["postcode"] = postcode
                parsed["address"] = f"{street}, {postcode}" if postcode else street
        return parsed

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    @api.model
    def _enrich_apply(self, record, found):
        """Write what `found` has, where `record` has nothing.

        `fill_empty`: an existing value is never replaced. Coordinates are
        written in the same run as the address, under the same rule.
        """
        values = {}
        if not record.rest_address and found.get("address"):
            values["rest_address"] = found["address"]
        if not record.geo_lat and found.get("lat") is not None:
            values["geo_lat"] = found["lat"]
        if not record.geo_lon and found.get("lon") is not None:
            values["geo_lon"] = found["lon"]
        if values:
            record.write(values)
        return values

    # ------------------------------------------------------------------
    # The server action
    # ------------------------------------------------------------------
    @api.model
    def action_enrich_addresses(self):
        """Fill empty addresses and positions from Visit Linköping, then OSM.

        Called as a server action from the list view, so it has no recordset:
        it works on every restaurant that has a name.

        Returns {"enriched": N, "uncertain": N, "not_found": N} and, when
        called from the UI, a notification with the same numbers. `uncertain`
        counts rows that were filled from a street-level hit — the address is
        written, but it is worth a look.
        """
        restaurants = self.search([("rest_name", "!=", False)])
        entries = self._enrich_index()

        enriched = uncertain = not_found = 0
        for restaurant in restaurants:
            # Nothing to do for a row that is already complete. Skipping it
            # here is what makes a second run report 0 enriched.
            if restaurant.rest_address and restaurant.geo_lat and restaurant.geo_lon:
                continue

            found = self._enrich_from_visitlinkoping(restaurant.rest_name, entries)
            if not found:
                found = self._enrich_from_nominatim(restaurant.rest_name)
            if not found:
                not_found += 1
                _logger.info(
                    "Enrichment: no address found for %r", restaurant.rest_name
                )
                continue

            written = self._enrich_apply(restaurant, found)
            if not written:
                # Found, but every field was already filled by hand. Not a
                # miss, and not an enrichment either.
                continue

            enriched += 1
            if not is_house_number_address(found.get("street")):
                uncertain += 1
                _logger.info(
                    "Enrichment: %r matched on street level (%s)",
                    restaurant.rest_name, found.get("street"),
                )

        result = {"enriched": enriched, "uncertain": uncertain, "not_found": not_found}
        _logger.info("Enrichment finished: %s", result)

        # A server action returns its value to the caller; the notification is
        # for the user who pressed the button.
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": _(
                    "%(enriched)s enriched, %(uncertain)s uncertain, "
                    "%(not_found)s not found"
                ) % result,
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
            "enrichment": result,
        }
