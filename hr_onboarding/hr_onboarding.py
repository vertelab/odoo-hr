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

    @api.multi
    def action_onboard_form(self):
        self.ensure_one()
        if self.onboard_stage_id.view_id and not self.onboard_stage_id.survey_id:
            view = self.env.ref('hr_onboarding.wizard_employee_form_hr_onboard_company_info')
            return {
                'type': 'ir.actions.act_window',
                'name': _('Update Company Info'),
                'key2': 'client_action_multi',
                'res_model': 'hr.employee.company.info.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'new',
                'context': {},
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


class survey_question(models.Model):
    _inherit = 'survey.question'

    fields_name = fields.Char(string='Fields Name', help='The fields will be used to save survey question.')


class survey_user_input(models.Model):
    _inherit = 'survey.user_input'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee')


class survey_user_input_line(models.Model):
    _inherit = 'survey.user_input_line'

    @api.model
    def save_lines(self, user_input_id, question, post, answer_tag):
        # TODO: catch question datas
        return super(survey_user_input_line, self).save_lines(user_input_id, question, post, answer_tag)


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

    department_id = fields.Char(string='Department', comodel_name='hr.department')
    job_id = fields.Char(string='Job', comodel_name='hr.job')

    @api.multi
    def confirm(self):
        pass


class WebsiteSurvey(WebsiteSurvey):

    def update_info_employee(self, survey, token):
        user_input = request.env['survey.user_input'].search([('survey_id', '=', survey.id), ('token', '=', token)])
        if user_input and user_input.employee_id:
            employee = user_input.employee_id
            vals = {}
            lines = user_input.user_input_line_ids.filtered(lambda l: not l.skipped)
            vals['name'] = '%s %s' %(lines.filtered(lambda l: l.question_id.fields_name == 'first_name').value_text, lines.filtered(lambda l: l.question_id.fields_name == 'last_name').value_text)
            gender = lines.filtered(lambda l: l.question_id.fields_name == 'gender').value_suggested.value
            if gender:
                vals['gender'] = gender.lower()
            vals['identification_id'] = lines.filtered(lambda l: l.question_id.fields_name == 'identification_id').value_text
            street = lines.filtered(lambda l: l.question_id.fields_name == 'street')
            zip = lines.filtered(lambda l: l.question_id.fields_name == 'zip')
            city = lines.filtered(lambda l: l.question_id.fields_name == 'city')
            if street or zip or city:
                address_home_id = employee.address_home_id
                if not address_home_id:
                    address_home_id = request.env['res.partner'].create({
                        'name': vals['name'],
                        'street': street.value_text or '',
                        'zip': zip.value_text or '',
                        'city': city.value_text or '',
                    })
                    vals['address_home_id'] = address_home_id.id
                else:
                    address_home_id.write({
                        'name': vals['name'],
                        'street': street.value_text or '',
                        'zip': zip.value_text or '',
                        'city': city.value_text or '',
                    })
            employee.write(vals)
            member_name_1 = lines.filtered(lambda l: l.question_id.fields_name == 'member_name_1')
            relation_1 = lines.filtered(lambda l: l.question_id.fields_name == 'relation_1')
            member_contact_1 = lines.filtered(lambda l: l.question_id.fields_name == 'member_contact_1')
            if member_name_1 or relation_1 or member_contact_1:
                if member_name_1:
                    member_name_1 = member_name_1.value_text
                if relation_1:
                    relation_1 = relation_1.value_suggested.value.lower()
                if member_contact_1:
                    member_contact_1 = member_contact_1.value_text
                fams = employee.fam_ids
                if len(fams) > 0:
                    member_1 = fams[0]
                    member_1.write({
                        'member_name': member_name_1 or '',
                        'relation': relation_1 or '',
                        'member_contact': member_contact_1 or '',
                    })
                else:
                    request.env['hr.employee.family'].create({
                        'member_name': member_name_1 or '',
                        'relation': relation_1 or '',
                        'member_contact': member_contact_1 or '',
                        'employee_id': employee.id,
                    })
            member_name_2 = lines.filtered(lambda l: l.question_id.fields_name == 'member_name_2')
            relation_2 = lines.filtered(lambda l: l.question_id.fields_name == 'relation_2')
            member_contact_2 = lines.filtered(lambda l: l.question_id.fields_name == 'member_contact_2')
            if member_name_2 or relation_2 or member_contact_2:
                if member_name_2:
                    member_name_2 = member_name_2.value_text
                if relation_2:
                    relation_2 = relation_2.value_suggested.value.lower()
                if member_contact_2:
                    member_contact_2 = member_contact_2.value_text
                fams = employee.fam_ids
                if len(fams) > 1:
                    member_2 = fams[1]
                    member_2.write({
                        'member_name': member_name_2 or '',
                        'relation': relation_2 or '',
                        'member_contact': member_contact_2 or '',
                    })
                else:
                    request.env['hr.employee.family'].create({
                        'member_name': member_name_2 or '',
                        'relation': relation_2 or '',
                        'member_contact': member_contact_2 or '',
                        'employee_id': employee.id,
                    })

    @http.route(['/survey/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        res = super(WebsiteSurvey, self).submit(survey, **post)
        self.update_info_employee(survey, post['token'])
        return res
