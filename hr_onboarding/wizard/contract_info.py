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


class hr_employee_contract_info_wizard(models.TransientModel):
    _name = 'hr.employee.contract.info.wizard'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee')
    partner_id = fields.Many2one(string='Home Address', comodel_name='res.partner')
    department_id = fields.Many2one(string='Department', comodel_name='hr.department')
    job_id = fields.Many2one(string='Job', comodel_name='hr.job')
    coach_id = fields.Many2one(string='Coach', comodel_name='hr.employee')
    manager = fields.Boolean(string='Manager')
    contract_type_id = fields.Many2one(string='Contract Type', comodel_name='hr.contract.type', required=True)
    struct_id = fields.Many2one(string='Contract Struct', comodel_name='hr.payroll.structure', required=True)
    trial_date_start = fields.Date(string='Trail Date Start')
    trial_date_end = fields.Date(string='Trail Date End')
    duration_date_start = fields.Date(string='Trail Date Start', required=True)
    duration_date_end = fields.Date(string='Trail Date End')
    working_hours = fields.Many2one(string='Work schedule', comodel_name='resource.calendar')
    wage = fields.Float(string='Wage', required=True)
    prel_tax_amount = fields.Float(string='Tax Amount')
    wage_tax_base = fields.Float(string='Wage Details')
    bank_id = fields.Many2one(string='Bank Accounts', comodel_name='res.partner.bank', domain="[('partner_id', '=', partner_id)]")

    @api.multi
    def confirm(self):
        employee = self.employee_id
        contracts = self.env['hr.contract'].search([('employee_id', '=', employee.id)])
        contract_vals = {
            'type_id': self.contract_type_id.id,
            'struct_id': self.struct_id.id,
            'trial_date_start': self.trial_date_start,
            'trial_date_end': self.trial_date_end,
            'date_start': self.duration_date_start,
            'date_end': self.duration_date_end,
            'working_hours': self.working_hours.id,
            'wage': self.wage,
            'prel_tax_amount': self.prel_tax_amount,
            'wage_tax_base': self.wage_tax_base,
        }
        if len(contracts) > 0:
            contract = contracts[0]
            contract.write(contract_vals)
        else:
            if not employee.identification_id:
                raise Warning(_('Configurate identification ID for employee %s') % employee.name)
            contract_vals.update({
                'name': '%s-1' % employee.identification_id,
                'employee_id': employee.id,
            })
            contract = self.env['hr.contract'].create(contract_vals)
        employee.write({
            'department_id': self.department_id.id,
            'job_id': self.job_id.id,
            'coach_id': self.coach_id.id,
            'manager': self.manager,
        })
        if self.bank_id:
            home = employee.address_home_id
            if not home:
                employee.write({
                    'address_home_id': self.bank_id.partner_id.id
                })
