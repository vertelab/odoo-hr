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

    # office_id for jobseekers and employers, not for administrative officers
    office_id = fields.Many2one(
        string="office", comodel_name="hr.department", index=True
    )


class ResUsers(models.Model):
    _inherit = "res.users"

    office_ids = fields.Many2many(
        comodel_name="hr.department", compute="_compute_office_ids"
    )

    @api.one
    def _compute_office_ids(self):
        for employee in self.employee_ids:
            self.office_ids |= employee.office_ids

    operation_ids = fields.Many2many(
        comodel_name="hr.operation", compute="_compute_operation_ids"
    )

    @api.one
    def _compute_operation_ids(self):
        for employee in self.employee_ids:
            self.operation_ids |= employee.operation_ids

    operation_names = fields.Char(
        string="Operations",

    )

    office_codes = fields.Char(
        string="Office codes",
        compute="compute_office_codes"
    )

    @api.multi
    def compute_office_codes(self):
        for rec in self:
            office_codes = []
            for e in rec.employee_ids:
                office_codes.append(e.office_codes)
            rec.office_codes = ",".join(office_codes)

    @api.multi
    def compute_operation_names(self):
        for rec in self:
            operation_names = []
            for e in rec.employee_ids:
                operation_names.append(e.operation_names)
            rec.operation_names = ",".join(operation_names)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # workplace
    operation_id = fields.Many2one(
        comodel_name="hr.operation", string="Operation", index=True
    )
    office_ids = fields.Many2many("hr.department", string="Offices", index=True)

    operation_ids = fields.Many2many(
        comodel_name="hr.operation", compute="_compute_operation_ids"
    )

    operation_names = fields.Char(
        string="Operations",
        compute="compute_operation_names",
        readonly=True,
        store=True
    )
    office_codes = fields.Char(string="Office codes",
                               compute="compute_office_codes",
                               readonly=True,
                               store=True)
    signature = fields.Char(string="Signature", related="user_id.login")

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
        for rec in self:
            res = super(HrEmployee, rec).write(vals)
            if "department_id" in vals:
                rec.update_office_ids()
            rec.compute_office_codes()
            rec.compute_operation_names()
            rec.compute_is_pdm_planner()
        return vals

    @api.multi
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        res.compute_office_codes()
        res.compute_operation_names()
        res.compute_is_pdm_planner()
        return res

    @api.multi
    def compute_operation_names(self):
        for rec in self:
            operation_names = []
            for operation in rec.operation_ids:
                operation_names.append(operation.name)
            if operation_names:
                operation_name_string = ",".join([str(code) for code in operation_names])
                if rec.operation_names != operation_name_string:
                    rec.operation_names = operation_name_string
            else:
                rec.operation_names = ""

    @api.multi
    def compute_office_codes(self):
        for rec in self:
            office_codes = []
            for office in rec.office_ids:
                office_codes.append(office.office_code)
            if office_codes:
                office_codes_string = ",".join([str(code) for code in office_codes])
                if office_codes_string != rec.office_codes:
                    rec.office_codes = office_codes_string
            else:
                rec.office_codes = ""

    @api.multi
    def compute_is_pdm_planner(self):
        for rec in self:
            _logger.info("office_codes %s" % rec.office_codes)
            if "0248" in rec.office_codes and not rec.user_id.has_group('af_security.af_meeting_planner_PDM'):
                rec.user_id.write({
                    'groups_id': [(4, self.env.ref('af_security.af_meeting_planner_PDM').id, 0)]
                })
            elif "0248" not in rec.office_codes and rec.user_id.has_group('af_security.af_meeting_planner_PDM'):
                rec.user_id.write({
                    'groups_id': [(3, self.env.ref('af_security.af_meeting_planner_PDM').id, 0)]
                })

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, vals_list):
        records = super(HrEmployee, self).create(vals_list)
        records.update_office_ids()
        return records
