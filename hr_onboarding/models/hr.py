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

    onboard_stage_id = fields.Many2one(string='Onboard Stage', comodel_name="hr.onboard.stage", track_visibility='onchange')
    onboard_response_ids = fields.One2many(comodel_name='survey.user_input', inverse_name='employee_id')
    email = fields.Char(string='Email', track_visibility='onchange')
    login = fields.Char(related='user_id.login', string='login', track_visibility='onchange')
    medical_status = fields.Text(string='Medical Status', track_visibility='onchange')

    @api.model
    def _read_group_onboard_stage_id(self, present_ids, domain, **kwargs):
        stages = self.env['hr.onboard.stage'].search([]).name_get()
        folded = {
            self.env.ref('hr_onboarding.state_benefits').id: True,
            self.env.ref('hr_onboarding.state_business_card').id: True,
            self.env.ref('hr_onboarding.state_completed').id: True,
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
                context.update(partner_detail) # pass in default partner data to context
            contract_detail = self.get_contract_detail(self)
            if len(contract_detail) > 0:
                context.update(contract_detail) # pass in default contract data to context
            if self.onboard_stage_id == self.env.ref('hr_onboarding.state_assets'):
                # if assets are set, go to tree view and configure.
                if len(self.assets_ids) > 0:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _('Update Assets'),
                        'key2': 'client_action_multi',
                        'res_model': 'account.asset.asset',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'view_ids': (6, 0, [self.env.ref('account_asset.view_account_asset_asset_tree').id, self.env.ref('account_asset.view_account_asset_asset_form').id]),
                        'search_view_id': self.env.ref('account_asset.view_account_asset_search').id,
                        'target': 'current',
                        'context': {'search_default_employee_id': self.id, 'default_employee_id': self.id},
                    }
            if self.onboard_stage_id == self.env.ref('hr_onboarding.state_certifications'):
                # if certifications are set, go to tree view and configure.
                if len(self.certification_ids) > 0:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _('Update Certifications'),
                        'key2': 'client_action_multi',
                        'res_model': 'hr.certification',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'view_ids': (6, 0, [self.env.ref('hr_certifications.view_hr_certification_tree_sign').id, self.env.ref('hr_certifications.view_hr_certification_form').id]),
                        'search_view_id': self.env.ref('hr_certifications.view_hr_certification_filter').id,
                        'target': 'current',
                        'context': {'search_default_employee_id': self.id, 'default_employee_id': self.id},
                    }
            return {
                'type': 'ir.actions.act_window',
                'name': self.onboard_stage_id.view_id.name,
                'key2': 'client_action_multi',
                'res_model': self.onboard_stage_id.view_id.model,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.onboard_stage_id.view_id.id,
                'target': 'new',
                'context': context,
            }
        if self.onboard_stage_id.survey_id and not self.onboard_stage_id.view_id:
            return self.action_start_survey()
    
    @api.multi
    def action_onboard_business_card_print(self):
        self.ensure_one()
        # print business card
        return {
            'type': 'ir.actions.report.xml',
            'id': self.env.ref('hr_onboarding.action_employee_business_card').id,
            'model': 'hr.employee',
            'report_type': 'scribus_pdf',
            'report_name': 'business_card.sla',
        }

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
