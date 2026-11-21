"""Restaurant discovery from OpenStreetMap.

The wizard asks Overpass for restaurants near the office and shows them as
suggestions. Nothing is created until the user ticks a row and presses "Add
selected": a discovery run proposes, it never adds to the catalogue.

Two rules shape the code:

- The external source is unstable. Overpass has three public mirrors and any
  of them can answer 502. All three are tried, and if none answers the user
  gets a clear message instead of a traceback — and the catalogue is untouched.
- A suggestion that is already in the catalogue is not a suggestion. Dedup runs
  on the normalised name plus the position, and on street plus cuisine for a
  restaurant that has been renamed.
"""

import json
import logging
import re
import urllib.parse
import urllib.request

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.hr_lunch.models.lunch_cuisine import apply_cuisine_tags, map_cuisine
from odoo.addons.hr_lunch.models.lunch_geo import haversine
from odoo.addons.hr_lunch.models.res_config_settings import NOMINATIM_USER_AGENT

_logger = logging.getLogger(__name__)

# Public Overpass mirrors, tried in order. The first is the reference
# instance; the other two are listed by the OSM wiki as public alternatives.
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
OVERPASS_TIMEOUT = 30

# A suggestion this close to an existing row is the same restaurant.
DEDUP_DISTANCE_M = 60

# Swedish letters folded to ASCII before comparing names. "Kebab-Huset" and
# "kebab huset" are the same name; so are "Östans" and "Ostans".
_FOLD = str.maketrans({"å": "a", "ä": "a", "ö": "o", "é": "e", "ü": "u"})
# Everything that is not a letter or a digit is a separator, so punctuation and
# spacing cannot make two spellings of one name differ.
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_name(name):
    """Comparison form of a restaurant name: lowercase, ASCII, alnum only."""
    if not name:
        return ""
    folded = name.strip().lower().translate(_FOLD)
    return _NON_ALNUM.sub(" ", folded).strip()


def normalize_street(address):
    """Comparison form of a street: the part before the first comma.

    OSM writes "Storgatan 5, Linköping" and the catalogue may hold
    "Storgatan 5" — the street is the part that survives a change of city
    formatting, so that is what is compared.
    """
    if not address:
        return ""
    street = address.split(",")[0]
    return _NON_ALNUM.sub(" ", street.lower().translate(_FOLD)).strip()


class LunchDiscoveryLine(models.TransientModel):
    _name = "lunch.discovery.line"
    _description = "A restaurant suggested by OpenStreetMap"
    _order = "distance_m, name"

    wizard_id = fields.Many2one(
        comodel_name="lunch.discovery.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    # Unchecked from the start: the spec is that a run proposes and the user
    # decides, so an untouched wizard creates nothing.
    selected = fields.Boolean(string="Add", default=False)
    name = fields.Char(string="Name")
    address = fields.Char(string="Address")
    cuisine = fields.Char(string="Cuisine")
    # The tag names the cuisine maps to, shown so the user sees what the
    # restaurant will be tagged with before adding it.
    cuisine_tags = fields.Char(string="Tags")
    distance_m = fields.Integer(string="Distance (m)")
    osm_id = fields.Char(string="OSM id")
    geo_lat = fields.Float(string="Latitude", digits=(10, 7))
    geo_lon = fields.Float(string="Longitude", digits=(10, 7))
    # Set when the row looks like a restaurant that is already in the
    # catalogue under another name. The row is shown, not hidden: the user
    # decides, and the flag says why it is worth a second look.
    possible_duplicate = fields.Char(string="Possible duplicate")


class LunchDiscoveryWizard(models.TransientModel):
    _name = "lunch.discovery.wizard"
    _description = "Find restaurants near the office"

    radius_m = fields.Integer(string="Radius (m)", default=2000)
    max_results = fields.Integer(string="Max results", default=50)
    line_ids = fields.One2many(
        comodel_name="lunch.discovery.line",
        inverse_name="wizard_id",
        string="Suggestions",
    )

    @api.model
    def _company_position(self):
        """(lat, lon) from ir.config_parameter, or (None, None).

        Same parameter as lunch.choice uses; the position has one home.
        """
        params = self.env["ir.config_parameter"].sudo()
        raw_lat = params.get_param("hr_lunch.company_lat", default="")
        raw_lon = params.get_param("hr_lunch.company_lon", default="")
        try:
            return float(raw_lat), float(raw_lon)
        except (TypeError, ValueError):
            return None, None

    def _overpass_query(self, lat, lon, radius_m):
        """Overpass QL for restaurants, fast food and cafés within the radius.

        One bbox around the radius, then an `around` filter: the bbox alone is
        a square, and a square with a 2 km half-side reaches 2.8 km at the
        corner.
        """
        # ~0.01 degrees is about 1.1 km of latitude; a slightly generous box
        # costs nothing and keeps the query simple.
        delta = (radius_m / 1000.0) / 100.0
        bbox = f"{lat - delta:.6f},{lon - delta:.6f},{lat + delta:.6f},{lon + delta:.6f}"
        return (
            "[out:json][timeout:25];"
            "("
            f'node["amenity"~"^(restaurant|fast_food|cafe)$"]({bbox})(around:{radius_m},{lat},{lon});'
            f'way["amenity"~"^(restaurant|fast_food|cafe)$"]({bbox})(around:{radius_m},{lat},{lon});'
            ");"
            "out center tags;"
        )

    def _fetch_overpass(self, query):
        """The Overpass payload, or None when no mirror answered.

        Every mirror is tried in order. A 502, a timeout and a broken JSON body
        are the same outcome here: try the next one. The error is logged with
        the mirror that failed, so a dead mirror is visible in the log.
        """
        data = urllib.parse.urlencode({"data": query}).encode("utf-8")
        for url in OVERPASS_MIRRORS:
            request = urllib.request.Request(
                url,
                data=data,
                headers={"User-Agent": NOMINATIM_USER_AGENT},
            )
            try:
                with urllib.request.urlopen(request, timeout=OVERPASS_TIMEOUT) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as error:  # network, timeout, 502, bad JSON
                _logger.warning("Overpass mirror %s failed: %s", url, error)
        return None

    @api.model
    def _element_position(self, element):
        """(lat, lon) for a node or a way, or (None, None).

        A way has no lat/lon of its own; `out center` gives the centre in
        `center`. Without a position the row cannot be deduplicated by
        distance, so it is dropped rather than guessed.
        """
        if element.get("type") == "node":
            return element.get("lat"), element.get("lon")
        center = element.get("center") or {}
        return center.get("lat"), center.get("lon")

    @api.model
    def _element_address(self, tags):
        """A readable address from OSM's address tags.

        OSM has no single address field; street, house number and city are
        separate tags and any of them can be missing. An empty result is
        honest — the row then shows no address, which is a real state.
        """
        street = tags.get("addr:street")
        number = tags.get("addr:housenumber")
        city = tags.get("addr:city")
        line = " ".join(part for part in (street, number) if part)
        if city:
            line = f"{line}, {city}" if line else city
        return line or None

    @api.model
    def _existing_restaurants(self):
        """The catalogue as a list of comparison records.

        Read once per run: a per-suggestion search would be one query per row
        for a table of a few dozen rows.
        """
        return [
            {
                "name": normalize_name(restaurant.rest_name),
                "street": normalize_street(restaurant.rest_address),
                # lunch.choice has no cuisine field; the cuisine lives in the
                # restaurant's cuisine tags. Compared as the set of tag names
                # the OSM value maps to, so a hand-added tag cannot match.
                "cuisine": self._cuisine_set(restaurant),
                "lat": restaurant.geo_lat,
                "lon": restaurant.geo_lon,
            }
            for restaurant in self.env["lunch.choice"].search([])
        ]

    @api.model
    def _cuisine_set(self, restaurant):
        """The restaurant's cuisine tags as a frozenset of names."""
        return frozenset(
            restaurant.tag_ids.filtered(
                lambda tag: tag.tag_type == "cuisine"
            ).mapped("name")
        )

    def _duplicate_reason(self, name, street, cuisine, lat, lon, existing):
        """Why a suggestion is already in the catalogue, or None.

        Two signals, both from the spec:
        - the same name and a position within DEDUP_DISTANCE_M: the same
          restaurant, hidden;
        - the same street and cuisine under another name: a renamed
          restaurant, shown with a flag so the user can judge.
        """
        normal_name = normalize_name(name)
        cuisine_set = frozenset(map_cuisine(cuisine))
        for row in existing:
            if not row["name"]:
                continue
            if (
                row["name"] == normal_name
                and row["lat"] and row["lon"]
                and haversine(row["lat"], row["lon"], lat, lon) < DEDUP_DISTANCE_M
            ):
                return "same"
            if street and row["street"] == street and cuisine_set & row["cuisine"]:
                return "renamed"
        return None

    def fetch_suggestions(self):
        """Ask Overpass for restaurants and fill the suggestion list.

        Suggestions that are already in the catalogue are dropped; suggestions
        that look like a renamed restaurant are kept and flagged. When no
        mirror answers, the user gets an error and the catalogue is untouched.
        """
        self.ensure_one()
        lat, lon = self._company_position()
        if lat is None:
            raise UserError(
                _("The office position is not set. Set it under Settings > "
                  "Lunch > Coordinates first — without it there is no radius "
                  "to search.")
            )

        payload = self._fetch_overpass(self._overpass_query(lat, lon, self.radius_m))
        if payload is None:
            raise UserError(
                _("Overpass is not answering — the catalogue is unchanged. "
                  "Try again later; no restaurant was added or changed.")
            )

        existing = self._existing_restaurants()
        seen_osm_ids = set()
        values = []
        for element in payload.get("elements") or []:
            tags = element.get("tags") or {}
            name = (tags.get("name") or "").strip()
            if not name:
                continue
            osm_id = f'{element.get("type")}/{element.get("id")}'
            if osm_id in seen_osm_ids:
                continue
            seen_osm_ids.add(osm_id)

            element_lat, element_lon = self._element_position(element)
            if element_lat is None or element_lon is None:
                continue
            distance = round(haversine(lat, lon, element_lat, element_lon))
            if distance > self.radius_m:
                continue

            address = self._element_address(tags)
            cuisine = (tags.get("cuisine") or "").strip().lower()
            reason = self._duplicate_reason(
                name, normalize_street(address), cuisine,
                element_lat, element_lon, existing,
            )
            if reason == "same":
                continue

            values.append({
                "name": name,
                "address": address,
                "cuisine": cuisine or None,
                "cuisine_tags": ", ".join(map_cuisine(cuisine)) or None,
                "distance_m": distance,
                "osm_id": osm_id,
                "geo_lat": element_lat,
                "geo_lon": element_lon,
                "possible_duplicate": (
                    _("Same street and cuisine as an existing restaurant")
                    if reason == "renamed" else None
                ),
            })

        values.sort(key=lambda row: row["distance_m"])
        values = values[: self.max_results]

        self.line_ids.unlink()
        self.env["lunch.discovery.line"].create(
            [dict(row, wizard_id=self.id) for row in values]
        )

        if not values:
            return self._notify(
                _("No new restaurants found within %(radius)s m.") % {"radius": self.radius_m},
                "warning",
            )
        return self._notify(
            _("%(count)s suggestions found. Tick the ones to add.")
            % {"count": len(values)},
            "success",
        )

    def action_add_selected(self):
        """Create a restaurant for each ticked suggestion and nothing else.

        The selection is the whole contract: an unticked row is a proposal the
        user declined. Without a tick nothing is created and the user is told.
        """
        self.ensure_one()
        selected = self.line_ids.filtered("selected")
        if not selected:
            return self._notify(
                _("No rows selected — nothing was added."), "warning"
            )

        Restaurant = self.env["lunch.choice"]
        created = Restaurant
        for line in selected:
            restaurant = Restaurant.create({
                "rest_name": line.name,
                "rest_address": line.address or False,
                "geo_lat": line.geo_lat,
                "geo_lon": line.geo_lon,
            })
            if line.cuisine:
                apply_cuisine_tags(restaurant, line.cuisine)
            created |= restaurant

        return self._notify(
            _("%(count)s restaurants added.") % {"count": len(created)}, "success"
        )

    @api.model
    def _notify(self, message, notification_type):
        """A notification action, so the wizard reports without a traceback."""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": notification_type,
                "message": message,
                "sticky": False,
            },
        }
