"""Menu link health for the lunch catalogue.

The rule is plain functions, no Odoo imports, so it can be tested without a
database -- the same split as lunch_geo. The model method below only fetches
and writes.

The module measures, it does not interpret: nothing about today's dishes is
read or stored. The question is only "is there a menu behind this link".
"""

import logging
import urllib.request

from odoo import api, fields, models

from .res_config_settings import NOMINATIM_USER_AGENT

_logger = logging.getLogger(__name__)

# A menu page is not a landing page. Below this many characters of text it is
# a shell -- a JS app, a cookie wall, or a redirect notice -- not a menu.
MIN_MENU_TEXT = 800

# Two weekdays is the smallest evidence of a weekly menu. Swedish and English,
# because the catalogue links to both.
WEEKDAYS = ('måndag', 'tisdag', 'onsdag', 'torsdag', 'fredag',
            'mon', 'tue', 'wed', 'thu', 'fri')
MIN_WEEKDAYS = 2

FETCH_TIMEOUT = 10
# Enough of a page to judge it; a menu is never announced after a megabyte.
MAX_READ_BYTES = 2000000


def is_pdf_url(url):
    """True when the URL itself says it is a PDF."""
    return (url or '').split('?')[0].strip().lower().endswith('.pdf')


def is_pdf_content_type(content_type):
    """True when the server answers with a PDF content type."""
    return 'application/pdf' in (content_type or '').lower()


def count_weekdays(text):
    """How many of WEEKDAYS occur in the text, case-insensitive."""
    lowered = (text or '').lower()
    return sum(1 for day in WEEKDAYS if day in lowered)


def classify_html(text):
    """Status for an HTML page: 'ok' when it is long enough and names two weekdays."""
    if len(text or '') > MIN_MENU_TEXT and count_weekdays(text) >= MIN_WEEKDAYS:
        return 'ok'
    return 'weak'


def classify_pdf(body):
    """Status for a PDF: 'ok' when the file actually arrived, else 'dead'.

    The content is not parsed. A PDF that downloads is a menu; whether it is
    this week's menu is not something this module claims to know.
    """
    return 'ok' if body else 'dead'


class LunchChoice(models.Model):
    _inherit = 'lunch.choice'

    # ------------------------------------------------------------------
    # Menu link health
    # ------------------------------------------------------------------
    @api.model
    def check_menus(self):
        """Check every menu link and write link_status + link_checked_at.

        One dead URL must never stop the run: every failure -- timeout, DNS,
        TLS, a 500, a body that cannot be decoded -- ends at 'dead' for that
        row and the loop continues. A cron that stops halfway leaves the
        catalogue in a state nobody can reason about.

        Returns a count per status, so the coverage can be compared with the
        measured baseline (~20 ok / ~24 weak or dead).
        """
        counts = {'ok': 0, 'weak': 0, 'dead': 0}
        restaurants = self.search([('link_to_menu', '!=', False)])
        now = fields.Datetime.now()

        for restaurant in restaurants:
            url = (restaurant.link_to_menu or '').strip()
            if not url:
                continue
            status = self._check_menu_url(url)
            restaurant.write({'link_status': status, 'link_checked_at': now})
            counts[status] += 1

        _logger.info(
            "Menu link health: %(ok)s ok, %(weak)s weak, %(dead)s dead",
            counts,
        )
        return counts

    @api.model
    def _check_menu_url(self, url):
        """Status for one URL. Never raises.

        A PDF is judged by whether the file arrives, and is never read as a
        page -- decoding a PDF as text would produce a length that means
        nothing.
        """
        if not url.startswith(('http://', 'https://')):
            # The catalogue accepts a bare domain (valid_url adds the scheme
            # on save), so a row written before that rule may still lack it.
            url = 'https://' + url

        try:
            request = urllib.request.Request(
                url, headers={'User-Agent': NOMINATIM_USER_AGENT}
            )
            with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT) as response:
                content_type = response.headers.get('Content-Type', '')
                body = response.read(MAX_READ_BYTES)

            if is_pdf_content_type(content_type) or is_pdf_url(url):
                return classify_pdf(body)

            charset = response.headers.get_content_charset() or 'utf-8'
            text = body.decode(charset, errors='replace')
            return classify_html(text)
        except Exception as error:  # timeout, DNS, HTTP error, bad charset
            _logger.info("Menu link %s is dead: %s", url, error)
            return 'dead'
