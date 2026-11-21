"""Company position for the lunch distance.

`res.company` has no latitude or longitude, and it should not grow one for a
lunch module. The position lives in ir.config_parameter instead, edited from
the Lunch settings block.
"""

import json
import logging
import urllib.parse
import urllib.request

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# OSM's usage policy requires a real User-Agent identifying the application.
# Without it Nominatim answers 403 and the feature looks broken.
NOMINATIM_USER_AGENT = "VertelLunchBot/1.0 (info@vertel.se)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_TIMEOUT = 10


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lunch_company_lat = fields.Float(
        string="Latitude",
        config_parameter="hr_lunch.company_lat",
        digits=(10, 7),
        help="Latitude of the office, in decimal degrees. Used as the origin "
             "for the lunch distance.",
    )
    lunch_company_lon = fields.Float(
        string="Longitude",
        config_parameter="hr_lunch.company_lon",
        digits=(10, 7),
        help="Longitude of the office, in decimal degrees. Used as the origin "
             "for the lunch distance.",
    )
    lunch_company_position_set = fields.Boolean(
        string="Position set",
        compute="_compute_lunch_company_position_set",
        help="Unset means every restaurant shows a distance of 0.",
    )

    @api.depends("lunch_company_lat", "lunch_company_lon")
    def _compute_lunch_company_position_set(self):
        for settings in self:
            # 0/0 is a real point in the Gulf of Guinea, but it is also what an
            # untouched float looks like. For a Swedish office it is certainly
            # unset, and the warning is worth more than the edge case.
            settings.lunch_company_position_set = bool(
                settings.lunch_company_lat and settings.lunch_company_lon
            )

    def action_geocode_company(self):
        """Fill the position from the company's address via Nominatim.

        Returns a notification action so the user sees what happened. A
        geocoding service that does not answer is a normal outcome, not a
        traceback: the coordinates are left untouched and the message says so.
        """
        self.ensure_one()
        company = self.env.company
        address = company._display_address(without_company=True).replace("\n", ", ")
        address = " ".join(address.split())
        if not address:
            raise UserError(
                _("The company has no address. Fill it in under Settings > "
                  "Companies first.")
            )

        query = urllib.parse.urlencode({"q": address, "format": "json", "limit": 1})
        request = urllib.request.Request(
            f"{NOMINATIM_URL}?{query}",
            headers={"User-Agent": NOMINATIM_USER_AGENT},
        )

        try:
            with urllib.request.urlopen(request, timeout=NOMINATIM_TIMEOUT) as response:
                results = json.loads(response.read().decode("utf-8"))
        except Exception as error:
            _logger.warning("Nominatim geocoding failed for %r: %s", address, error)
            raise UserError(
                _("Could not reach the geocoding service. The position is "
                  "unchanged — enter the coordinates by hand if this keeps "
                  "happening.")
            ) from error

        if not results:
            raise UserError(
                _("No position found for the company address: %s") % address
            )

        self.lunch_company_lat = float(results[0]["lat"])
        self.lunch_company_lon = float(results[0]["lon"])
        # The wizard is transient; the values reach ir.config_parameter when
        # the user saves. Say so, rather than let the button look like a save.
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": _("Position found: %(lat)s, %(lon)s — save to keep it.")
                           % {"lat": self.lunch_company_lat, "lon": self.lunch_company_lon},
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
