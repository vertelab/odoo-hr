# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPulseSurvey(models.Model):
    _name = 'hr.pulse.survey'
    _description = 'Pulse Survey Campaign'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    survey_id = fields.Many2one('survey.survey', required=True, string="Survey",
                                domain=[('state', '=', 'open')])
    department_ids = fields.Many2many('hr.department', string="Departments")
    frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ], default='monthly', required=True)
    next_run_date = fields.Date()
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
    ], default='draft')
    response_ids = fields.One2many('survey.user_input', 'pulse_survey_id',
                                    string="Responses")
    response_count = fields.Integer(compute='_compute_response_count')

    # Alarm thresholds
    alarm_enabled = fields.Boolean(default=False)
    alarm_threshold = fields.Float(default=30.0, string="Alarm Threshold (%)",
                                    help="Trigger alarm when satisfaction drops below this %")
    alarm_recipient_ids = fields.Many2many('res.users', string="Alarm Recipients")

    def action_activate(self):
        self.write({'state': 'active', 'next_run_date': fields.Date.today()})

    def action_pause(self):
        self.write({'state': 'paused'})

    @api.depends('response_ids')
    def _compute_response_count(self):
        for rec in self:
            rec.response_count = len(rec.response_ids)

    def _cron_run_surveys(self):
        """Called by cron job. Sends surveys to employees in active campaigns."""
        today = fields.Date.today()
        campaigns = self.search([
            ('state', '=', 'active'),
            ('next_run_date', '<=', today),
        ])
        for campaign in campaigns:
            employees = self.env['hr.employee'].search([
                ('department_id', 'in', campaign.department_ids.ids),
            ]) if campaign.department_ids else self.env['hr.employee'].search([])
            for emp in employees:
                if emp.user_id and emp.work_email:
                    campaign.survey_id._send_mail(emp.user_id.partner_id)
            # Schedule next run
            delta = {'weekly': 7, 'biweekly': 14, 'monthly': 30,
                     'quarterly': 90}.get(campaign.frequency, 30)
            campaign.next_run_date = fields.Date.add(today, days=delta)

    def action_view_responses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'survey.user_input',
            'domain': [('pulse_survey_id', '=', self.id)],
            'name': _('Responses'),
            'view_mode': 'list,form',
        }

    def action_check_alarms(self):
        """Check if satisfaction is below threshold and notify."""
        for campaign in self:
            if not campaign.alarm_enabled or not campaign.response_ids:
                continue
            # Calculate average satisfaction score (assuming question 1 = satisfaction 1-5)
            responses = campaign.response_ids.filtered(
                lambda r: r.scoring_percentage is not None)
            if responses:
                avg = sum(r.scoring_percentage for r in responses) / len(responses)
                if avg < campaign.alarm_threshold:
                    for user in campaign.alarm_recipient_ids:
                        campaign.message_post(
                            body=_('⚠️ Pulse survey "%s" satisfaction is at %.1f%% '
                                   '(below threshold %.1f%%). Action may be needed.') % (
                                campaign.name, avg, campaign.alarm_threshold),
                            partner_ids=[user.partner_id.id],
                        )


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    pulse_survey_id = fields.Many2one('hr.pulse.survey', string="Pulse Survey",
                                       ondelete='set null')
