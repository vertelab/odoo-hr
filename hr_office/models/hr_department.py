# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = "hr.department"

    office_code = fields.Char(string="Office code")  # fyrställig
    organisation_number = fields.Char(string="Organisaiton Number")  # verksamhetsnummer
    operation_ids = fields.One2many(
        comodel_name="hr.operation", string="Operations", inverse_name="department_id"
    )
    partner_id = fields.Many2one(comodel_name="res.partner")
    employee_ids = fields.Many2many(string="Employees", comodel_name="hr.employee")


class HrOperation(models.Model):
    _name = "hr.operation"

    name = fields.Char(string="Name")
    opening_hours = fields.Char(string="Opening hours")
    personal_service_opening = fields.Char(string="Opening hours for personal service")
    operation_code = fields.Char(string="Operation Code")

    department_id = fields.Many2one(comodel_name="hr.department", string="Office")
    accessibilites_ids = fields.One2many(
        comodel_name="hr.location.accessibility", inverse_name="operation_id"
    )

    partner_id = fields.Many2one("res.partner", string="Partner")
    visitation_address_id = fields.Many2one("res.partner", string="Visitation address")
    mailing_address_id = fields.Many2one("res.partner", string="Mailing address")

    visitation_address_street = fields.Char(
        string="Street", related="visitation_address_id.street"
    )
    visitation_address_city = fields.Char(
        string="City", related="visitation_address_id.city"
    )
    visitation_address_zip = fields.Char(
        string="Zip", related="visitation_address_id.zip"
    )

    location_id = fields.Many2one(comodel_name="hr.location", string="Location")

    workplace_number = fields.Char(
        string="Workplace number", related="location_id.workplace_number"
    )
    location_code = fields.Char(
        string="Location code", related="location_id.location_code"
    )

    employee_ids = fields.One2many(
        string="Employees", comodel_name="hr.employee", inverse_name="operation_id"
    )


class HrLocation(models.Model):
    _name = "hr.location"
    name = fields.Char(string="Name")
    location_code = fields.Char(string="Location code")
    workplace_number = fields.Char(string="Workplace number")

    visitation_address_id = fields.Many2one("res.partner", string="Visitation address")

    visitation_address_street = fields.Char(
        string="Street", related="visitation_address_id.street"
    )
    visitation_address_city = fields.Char(
        string="City", related="visitation_address_id.city"
    )
    visitation_address_zip = fields.Char(
        string="Zip", related="visitation_address_id.zip"
    )

    operation_ids = fields.One2many(
        comodel_name="hr.operation", string="Operations", inverse_name="location_id"
    )

    @api.model
    def get_workplace_number(self, location_code):
        location = self.search([("location_code", "=", location_code)])
        if location:
            return location.workplace_number
        else:
            return False


class HrlocationAccessibility(models.Model):
    _name = "hr.location.accessibility"

    operation_id = fields.Many2one(comodel_name="hr.operation")
    name = fields.Char(string="Type")
    description = fields.Char(string="Description")