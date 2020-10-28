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


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    #office_id for jobseekers and employers, not for administrative officers
    office_id = fields.Many2one(string="office", comodel_name="hr.department")
    
class ResUsers(models.Model):
    _inherit = "res.users"

    office_ids = fields.Many2many(comodel_name="hr.department", compute="_compute_office_ids")

    @api.one
    def _compute_office_ids(self):
        for employee in self.employee_ids:
            self.office_ids |= employee.office_ids

    operation_ids = fields.Many2many(comodel_name="hr.operation", compute="_compute_operation_ids")

    @api.one
    def _compute_operation_ids(self):
        for employee in self.employee_ids:
            self.operation_ids |= employee.operation_ids

    office_codes = fields.Char(string="Office codes", compute="compute_office_codes", readonly=True)

    @api.one
    def compute_office_codes(self):
        office_codes = []
        for office in self.office_ids:
            office_codes.append(office.office_code)
        if office_codes:
            self.office_codes = ','.join([str(code) for code in office_codes]) 
        else:
            self.office_codes = ""



class HrEmployee(models.Model):
    _inherit = "hr.employee"

    operation_id = fields.Many2one(comodel_name="hr.operation", string="Operation") #workplace

    office_ids = fields.Many2many(
        'hr.department', string='Offices')


    operation_ids = fields.Many2many(comodel_name="hr.operation", compute="_compute_operation_ids")

    @api.one
    def _compute_operation_ids(self):
        for office in self.office_ids:
            self.operation_ids |= office.operation_ids

    @api.one
    # @api.onchange('department_id')
    def update_office_ids(self):
        """Add department_id to office_ids."""
        if self.department_id not in self.office_ids:
            self.office_ids |= self.department_id

    @api.multi
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if 'department_id' in vals:
            self.update_office_ids()
        return vals

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        records = super(HrEmployee, self).create(vals_list)
        records.update_office_ids()
        return records
