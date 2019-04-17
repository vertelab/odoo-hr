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


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    onboard_stage_id = fields.Many2one(comodel_name="hr.onboard.stage")
    onboard_response_ids = fields.One2many(comodel_name='survey.user_input', inverse_name='employee_id')
    email = fields.Char(string='Email', track_visibility='onchange')
    login = fields.Char(related='user_id.login', string='login', track_visibility='onchange')
    medical_status = fields.Text(string='Medical Status', track_visibility='onchange')

    @api.model
    def _read_group_onboard_stage_id(self, present_ids, domain, **kwargs):
        stages = self.env['hr.onboard.stage'].search([]).name_get()
        folded = {
            self.env.ref('hr_onboarding.state_completed').id: True
        }
        return stages, folded

    _group_by_full = {
        'onboard_stage_id': _read_group_onboard_stage_id
    }

    # default value in wizard
    @api.model
    def get_partner_detail(self, employee):
        res = {}
        home_address = self.address_home_id
        if home_address:
            res.update({'default_partner_id': home_address.id})
        banks = home_address.bank_ids
        if len(banks) > 0:
            res.update({'default_bank_id': banks[0].id})
        return res

    # default value in wizard
    @api.model
    def get_contract_detail(self, employee):
        res = {
            'default_department_id': employee.department_id.id if employee.department_id else None,
            'default_job_id': employee.job_id.id if employee.job_id else None,
            'default_coach_id': employee.coach_id.id if employee.coach_id else None,
            'default_manager': employee.manager,
        }
        contracts = self.env['hr.contract'].search([('employee_id', '=', employee.id)])
        contract = contracts[0] if len(contracts) > 0 else None
        if contract:
            res.update({
                'default_contract_type_id': contract.type_id.id if contract.type_id else None,
                'default_struct_id': contract.struct_id.id if contract.struct_id else None,
                'default_trial_date_start': contract.trial_date_start or '',
                'default_trial_date_end': contract.trial_date_end or '',
                'default_duration_date_start': contract.date_start or '',
                'default_duration_date_end': contract.date_end or '',
                'default_working_hours': contract.working_hours.id if contract.working_hours else None,
                'default_wage': contract.wage,
                'default_prel_tax_amount': contract.prel_tax_amount,
                'default_wage_tax_base': contract.wage_tax_base,
            })
        return res

    # default value in wizard
    @api.model
    def get_certification_detail(self, employee):
        res = {
            'default_department_id': employee.department_id.id if employee.department_id else None,
            'default_job_id': employee.job_id.id if employee.job_id else None,
            'default_coach_id': employee.coach_id.id if employee.coach_id else None,
            'default_manager': employee.manager,
        }
        return res

    @api.multi
    def action_onboard_form(self):
        self.ensure_one()
        if self.onboard_stage_id.view_id and not self.onboard_stage_id.survey_id:
            context = {
                'default_employee_id': self.id,
            }
            partner_detail = self.get_partner_detail(self)
            if len(partner_detail) > 0:
                context.update(partner_detail)
            contract_detail = self.get_contract_detail(self)
            if len(contract_detail) > 0:
                context.update(contract_detail)
            wizard_id = 0
            if self.onboard_stage_id == self.env.ref('hr_onboarding.state_certifications'):
                if len(self.job_id.certification_type_ids) > 0:
                    cert = self.env['hr.employee.certification.wizard'].create({'employee_id': self.id})
                    for t in self.job_id.certification_type_ids:
                        self.env['hr.employee.certification.line.wizard'].create({
                            'employee_certification_wizard_id': cert.id,
                            'cert_type_id': t.id,
                        })
                    wizard_id = cert.id
            return {
                'type': 'ir.actions.act_window',
                'name': self.onboard_stage_id.view_id.name,
                'key2': 'client_action_multi',
                'res_model': self.onboard_stage_id.view_id.model,
                'res_id': wizard_id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.onboard_stage_id.view_id.id,
                'target': 'new',
                'context': context,
            }
        if self.onboard_stage_id.survey_id and not self.onboard_stage_id.view_id:
            return self.action_start_survey()

    @api.multi
    def action_start_survey(self):
        self.ensure_one()
        survey_obj = self.env['survey.survey']
        response_obj = self.env['survey.user_input']
        survey = self.onboard_stage_id.survey_id
        if survey:
            response = self.onboard_response_ids.with_context(survey=survey).filtered(lambda r: r.survey_id == r._context.get('survey'))
            if not response:
                # create a response and link it to this employee
                response = response_obj.create({'survey_id': survey.id, 'employee_id': self.id})
                self.onboard_response_ids = [(6, 0, [response.id])]
            else:
                response = response[0]
        return self.onboard_stage_id.survey_id.with_context(survey_token=response.token).action_start_survey()


class hr_job(models.Model):
    _inherit = 'hr.job'

    has_mobile_pad = fields.Boolean(string='Has Mobile/Pad')
    has_computer = fields.Boolean(string='Has Computer')
    has_key = fields.Boolean(string='Has Key')
    certification_type_ids = fields.Many2many(string='Certification Types', comodel_name='hr.certification.type')


class hr_onboard_stage(models.Model):
    """
   Stages in onboarding
    """
    _name = 'hr.onboard.stage'
    _description = "Onboard Stage"

    name = fields.Char(string='Name', required=True)
    technical_name = fields.Char(string='Technical Name', required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer(string='Color Index')
    fold = fields.Boolean(string='Folded in Kanban View', help='This stage is folded in the kanban view when there are no records in that state to display.')
    view_id = fields.Many2one(comodel_name='ir.ui.view', strig='View')
    survey_id = fields.Many2many(comodel_name='survey.survey', string='Survey')


class survey_user_input(models.Model):
    _inherit = 'survey.user_input'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee')


class hr_employee_company_info_wizard(models.TransientModel):
    _name = 'hr.employee.company.info.wizard'

    user_name = fields.Char(string='User Name', help='Name for login', required=True)
    password = fields.Char(string='Password', required=True)
    confirm_password = fields.Char(string='Confirm Password', required=True)
    email = fields.Char(string='Email', required=True)

    @api.multi
    def confirm(self):
        # TODO: check password
        pass


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


class hr_employee_assets_wizard(models.TransientModel):
    _name = 'hr.employee.assets.wizard'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee')
    mobile_pad_ids = fields.One2many(string='Mobile/Pad', comodel_name='hr.employee.assets.line.wizard', inverse_name='mobile_pad_employee_assets_wizard_id')
    computer_ids = fields.One2many(string='Computer', comodel_name='hr.employee.assets.line.wizard', inverse_name='computer_employee_assets_wizard_id')
    entry_ids = fields.One2many(string='Entry', comodel_name='hr.employee.assets.line.wizard', inverse_name='entry_employee_assets_wizard_id')
    has_mobile_pad = fields.Boolean(string='Has Mobile/Pad', related='employee_id.job_id.has_mobile_pad')
    has_computer = fields.Boolean(string='Has Computer', related='employee_id.job_id.has_computer')
    has_key = fields.Boolean(string='Has Key', related='employee_id.job_id.has_key')

    @api.multi
    def confirm(self):
        for a in self.mobile_pad_ids:
            a.mobile_pad_id.employee_id = self.employee_id.id
            a.mobile_pad_id.is_signed = a.mobile_pad_is_signed
        for c in self.computer_ids:
            c.computer_id.employee_id = self.employee_id.id
            c.computer_id.is_signed = c.computer_is_signed
        for e in self.entry_ids:
            e.entry_id.employee_id = self.employee_id.id
            e.entry_id.is_signed = e.entry_is_signed


class hr_employee_assets_line_wizard(models.TransientModel):
    _name = 'hr.employee.assets.line.wizard'

    mobile_pad_employee_assets_wizard_id = fields.Many2one(comodel_name='hr.employee.assets.wizard')
    mobile_pad_category = fields.Many2one(string='Mobile/Pad Category', comodel_name='account.asset.category', domain="[('journal_id.type', '=', 'purchase'), ('account_asset_id.user_type.code', '=', 'asset')]")
    mobile_pad_id = fields.Many2one(string='Mobile/pad', comodel_name='account.asset.asset', domain="[('employee_id', '=', False), ('category_id', '=', mobile_pad_category), ('state', '=', 'draft')]")
    mobile_pad_is_signed = fields.Boolean(string='Signed')
    computer_employee_assets_wizard_id = fields.Many2one(comodel_name='hr.employee.assets.wizard')
    computer_category = fields.Many2one(string='Computer Category', comodel_name='account.asset.category', domain="[('journal_id.type', '=', 'purchase'), ('account_asset_id.user_type.code', '=', 'asset')]")
    computer_id = fields.Many2one(string='Computer', comodel_name='account.asset.asset', domain="[('employee_id', '=', False), ('category_id', '=', computer_category), ('state', '=', 'draft')]")
    computer_is_signed = fields.Boolean(string='Signed')
    entry_employee_assets_wizard_id = fields.Many2one(comodel_name='hr.employee.assets.wizard')
    entry_category = fields.Many2one(string='Entry Category', comodel_name='account.asset.category', domain="[('journal_id.type', '=', 'purchase'), ('account_asset_id.user_type.code', '=', 'asset')]")
    entry_id = fields.Many2one(string='Entry', comodel_name='account.asset.asset', domain="[('employee_id', '=', False), ('category_id', '=', entry_category), ('state', '=', 'draft')]")
    entry_is_signed = fields.Boolean(string='Signed')


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


class WebsiteSurvey(WebsiteSurvey):

    @http.route(['/survey/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        res = super(WebsiteSurvey, self).submit(survey, **post)
        user_input = request.env['survey.user_input'].search([('token', '=', post['token'])])
        if user_input.employee_id:
            user_input.save_values('employee_id')
        return res

    @http.route(['/survey/check/<string:token>'], type='http', methods=['GET'], auth='public', website=True)
    def check(self, token, **post):
        user_input = request.env['survey.user_input'].search([('token', '=', token)])
        if user_input.employee_id:
            user_input.save_values('employee_id')
        return 'Hello World'
