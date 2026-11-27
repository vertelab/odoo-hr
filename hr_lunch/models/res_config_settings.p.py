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
        # res.company is not a res.partner -- it inherits format.address.mixin
        # and carries the address on partner_id. Calling _display_address() on
        # the company raised AttributeError on every click, so the button never
        # reached Nominatim at all.
        company = self.env.company
        address = company.partner_id._display_address(without_company=True)
        address = " ".join(address.replace("\n", ", ").split())
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

        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])

        # Write through, do not just fill the widget. res.config.settings is a
        # TransientModel: the row is dropped when the dialog closes, and the
        # only path to ir.config_parameter is set_values(), which runs on Save.
        # Filling the field and closing therefore saved nothing -- the button
        # looked like a save and was not one. The user still has to press Save
        # for the rest of the page, but the coordinates are already stored.
        params = self.env["ir.config_parameter"].sudo()
        # #if VERSION >= "20.0"
        params.set_str("hr_lunch.company_lat", lat)
        params.set_str("hr_lunch.company_lon", lon)
        # #else
        params.set_param("hr_lunch.company_lat", lat)
        params.set_param("hr_lunch.company_lon", lon)
        # #endif

        # The form is still showing the old numbers. Reload it instead of
        # closing: a closed dialog hides the result, and a stale form invites
        # the user to save the values they had before.
        self.lunch_company_lat = lat
        self.lunch_company_lon = lon
        return self._reload_settings(
            _("Position found and saved: %(lat)s, %(lon)s")
            % {"lat": lat, "lon": lon}
        )

    def _reload_settings(self, message):
        """Reload the settings form so it shows what was just written.

        act_window_close would drop the transient row and hide the result.
        soft_reload restores the current controller, which re-runs default_get
        and reads ir.config_parameter back into the fields -- the same chain
        account and payment_razorpay_oauth use after writing a setting from a
        button.
        """
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": message,
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }
