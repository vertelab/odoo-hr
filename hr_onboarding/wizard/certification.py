# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP,  Open Source Management Solution,  third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation,  either version 3 of the
#    License,  or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not,  see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.survey.controllers.main import WebsiteSurvey
from openerp.exceptions import except_orm, Warning
import logging
_logger = logging.getLogger(__name__)


class hr_employee_certification_wizard(models.TransientModel):
    _name = 'hr.employee.certification.wizard'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee')
    certification_ids = fields.One2many(string='Certification', comodel_name='hr.employee.certification.line.wizard', inverse_name='employee_certification_wizard_id')

    @api.multi
    def confirm(self):
        pass
        for c in self.certification_ids:
            self.env['hr.certification'].create({
                'name': u'%s' %c.cert_type_id.name,
                'employee_id': self.employee_id.id,
                'type_id': c.cert_type_id.id,
                'is_signed': c.cert_is_signed,
                'date_start': c.cert_date_start,
                'date_end': c.cert_date_end,
                'template': c.cert_type_id.template,
                'description': c.cert_type_id.description,
                'state': c.cert_state if c.cert_state else 'draft',
            })


class hr_employee_certification_line_wizard(models.TransientModel):
    _name = 'hr.employee.certification.line.wizard'

    employee_certification_wizard_id = fields.Many2one(comodel_name='hr.employee.certification.wizard')
    cert_type_id = fields.Many2one(string='Type', comodel_name='hr.certification.type', required=True)
    cert_is_signed = fields.Boolean(string='Signed')
    cert_date_start = fields.Date(string='Start')
    cert_date_end = fields.Date(string='End')
    cert_state = fields.Selection(selection=[('draft', 'Draft'), ('pending', 'Pending'), ('active', 'Active'), ('canceled', 'Canceled')], default='draft')
