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
    


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    operation_id = fields.Many2one("hr.operation", string="Operation")

    department_ids = fields.Many2many("hr.department", string="Office")
    
    office_codes = fields.Char(string="Office codes", compute="compute_office_codes")

    @api.one
    def compute_office_codes(self):
        office_codes = []
        for office in self.department_ids:
            office_codes.append(office.office_code)
        if office_codes:
            self.office_codes = ','.join([str(code) for code in office_codes]) 
        else:
            self.office_codes = ""
