# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCompanyPosition(TransactionCase):
    """Fetch from company address must store the coordinates, not fill a field.

    The button lives in res.config.settings, a TransientModel. Filling the
    widget and closing the dialog saves nothing: the row is dropped and only
    set_values() -- which runs on Save -- reaches ir.config_parameter. So the
    assertion is on the parameter, never on the field.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.param = cls.env["ir.config_parameter"].sudo()
        cls.settings = cls.env["res.config.settings"].create({})
        cls.env.company.write({
            "street": "Sveavägen 1",
            "zip": "111 57",
            "city": "Stockholm",
            "country_id": cls.env.ref("base.se").id,
        })

    def setUp(self):
        super().setUp()
        self._set("hr_lunch.company_lat", "")
        self._set("hr_lunch.company_lon", "")

    def _set(self, key, value):
        # get_param/set_param are gone in 20.0, replaced by get_str/set_str.
        if hasattr(self.param, "set_str"):
            self.param.set_str(key, value)
        else:
            self.param.set_param(key, value)

    def _get(self, key):
        if hasattr(self.param, "get_str"):
            return self.param.get_str(key, default="")
        return self.param.get_param(key, default="")

    def _geocode(self, payload):
        """Call the action with Nominatim stubbed out."""
        response = type("R", (), {
            "read": lambda self: payload,
            "__enter__": lambda self: self,
            "__exit__": lambda *a: False,
        })()
        with patch("urllib.request.urlopen", return_value=response):
            return self.settings.action_geocode_company()

    def test_coordinates_are_stored(self):
        """The button writes ir.config_parameter -- this is the reported bug."""
        self._geocode(b'[{"lat": "59.3326", "lon": "18.0649"}]')

        self.assertAlmostEqual(
            float(self._get("hr_lunch.company_lat")), 59.3326, places=4
        )
        self.assertAlmostEqual(
            float(self._get("hr_lunch.company_lon")), 18.0649, places=4
        )

    def test_stored_position_is_what_the_distance_uses(self):
        """lunch.choice reads the same parameter; the two must not diverge."""
        self._geocode(b'[{"lat": "59.3326", "lon": "18.0649"}]')
        lat, lon = self.env["lunch.choice"]._company_position()
        self.assertAlmostEqual(lat, 59.3326, places=4)
        self.assertAlmostEqual(lon, 18.0649, places=4)

    def test_nothing_is_written_when_geocoding_fails(self):
        """A service that does not answer must not clear a position the user set."""
        self._set("hr_lunch.company_lat", "57.7089")
        self._set("hr_lunch.company_lon", "11.9746")

        response = type("R", (), {
            "read": lambda self: b"",
            "__enter__": lambda self: self,
            "__exit__": lambda *a: False,
        })()
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(UserError):
                self.settings.action_geocode_company()

        self.assertEqual(
            float(self._get("hr_lunch.company_lat")), 57.7089
        )

    def test_company_without_address_raises_and_writes_nothing(self):
        """Country alone is still an address, so clear the whole thing.

        A company that only has a country would geocode to the centre of that
        country -- wrong, but not the empty case this test is about.
        """
        self.env.company.partner_id.write({
            "street": False,
            "street2": False,
            "zip": False,
            "city": False,
            "state_id": False,
            "country_id": False,
        })
        with self.assertRaises(UserError):
            self.settings.action_geocode_company()
        self.assertFalse(self._get("hr_lunch.company_lat"))
