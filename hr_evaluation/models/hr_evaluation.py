# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEvaluation(models.Model):
    _name = 'hr.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Evaluation"
    _order = 'state, date_planned, id desc'
    _rec_name = 'employee_id'

    active = fields.Boolean(default=True)

    # Employee data
    employee_id = fields.Many2one(
        'hr.employee', required=True, string="Employee",
        index=True, ondelete='cascade',
        default=lambda self: self._default_employee())
    employee_user_id = fields.Many2one('res.users', related='employee_id.user_id')
    manager_id = fields.Many2one(
        'hr.employee', string="Manager",
        default=lambda self: self._default_manager(),
        domain="[('id', '!=', employee_id)]")
    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True)

    # Plan
    plan_id = fields.Many2one('hr.evaluation.plan', string="Evaluation Plan")

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('self_evaluation', 'Self-evaluation'),
        ('manager_evaluation', 'Manager Evaluation'),
        ('meeting', 'Meeting Scheduled'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, required=True, copy=False)

    # Dates
    date_planned = fields.Date(string="Planned Date", default=fields.Date.today)
    date_self = fields.Date(string="Self-evaluation Date")
    date_manager = fields.Date(string="Manager Evaluation Date")
    date_meeting = fields.Datetime(string="Meeting Date")
    date_done = fields.Date(string="Completion Date")

    # Self-evaluation (embedded)
    self_achievements = fields.Text(string="What went well?")
    self_challenges = fields.Text(string="What was challenging?")
    self_improvements = fields.Text(string="What can be improved?")
    self_development = fields.Text(string="Development wishes")
    self_support = fields.Text(string="Support needed")
    self_career = fields.Text(string="Career goals (1-3 years)")
    self_wellbeing = fields.Selection([
        ('1','1 - Poor'),('2','2'),('3','3 - OK'),('4','4'),('5','5 - Great')
    ], string="Wellbeing / workload")
    self_engagement = fields.Selection([
        ('1','1 - Low'),('2','2'),('3','3 - OK'),('4','4'),('5','5 - High')
    ], string="Engagement / motivation")

    # Manager evaluation
    manager_feedback = fields.Html(string="Manager's Feedback")
    manager_strengths = fields.Text(string="Strengths")
    manager_areas_for_growth = fields.Text(string="Areas for Growth")

    # Final ratings
    final_rating = fields.Selection([
        ('1', '1 - Below Expectations'),
        ('2', '2 - Needs Improvement'),
        ('3', '3 - Meets Expectations'),
        ('4', '4 - Exceeds Expectations'),
        ('5', '5 - Outstanding'),
    ], string="Final Rating")

    # Meeting
    meeting_notes = fields.Html(string="Meeting Notes")
    action_items = fields.Html(string="Action Items")

    # Sign-off
    employee_signed = fields.Boolean(string="Employee Signed")
    employee_signed_date = fields.Datetime()
    manager_signed = fields.Boolean(string="Manager Signed")
    manager_signed_date = fields.Datetime()

    # Survey responses (for integration with Odoo survey module)
    self_survey_response_id = fields.Many2one('survey.user_input', string="Self Survey Response")
    manager_survey_response_id = fields.Many2one('survey.user_input', string="Manager Survey Response")

    # Goal links (placeholder for hr_evaluation_goal extension)
    goal_ids = fields.One2many('hr.evaluation.goal', 'evaluation_id', string="Goals")
    goal_count = fields.Integer(compute='_compute_goal_count')

    @api.depends('goal_ids')
    def _compute_goal_count(self):
        for rec in self:
            rec.goal_count = len(rec.goal_ids)

    # Skill assessment links (placeholder for hr_evaluation_skill extension)
    skill_assessment_ids = fields.One2many('hr.evaluation.skill', 'evaluation_id', string="Skills")
    skill_count = fields.Integer(compute='_compute_skill_count')

    @api.depends('skill_assessment_ids')
    def _compute_skill_count(self):
        for rec in self:
            rec.skill_count = len(rec.skill_assessment_ids)

    def _default_employee(self):
        if self.env.context.get('active_model') == 'hr.employee' and 'active_id' in self.env.context:
            return self.env.context['active_id']
        return self.env.user.employee_id.id if self.env.user.employee_id else False

    def _default_manager(self):
        emp = self.env.user.employee_id
        return emp.parent_id.id if emp else False

    # ---- State transitions ----

    def action_plan(self):
        """Move from draft to planned."""
        self.write({'state': 'planned'})

    def action_start_self(self):
        """Start self-evaluation phase."""
        self.write({'state': 'self_evaluation'})
        # Notify employee
        self._notify_employee_self_evaluation()

    def action_submit_self(self):
        """Employee submits self-evaluation."""
        self.ensure_one()
        if not self.self_achievements and not self.self_development:
            raise UserError(_("Please fill in at least 'What went well?' or 'Development wishes' before submitting."))
        self.write({
            'state': 'manager_evaluation',
            'date_self': fields.Date.today(),
        })
        # Notify manager
        self._notify_manager_evaluation()

    def action_submit_manager(self):
        """Manager submits evaluation."""
        self.write({
            'state': 'meeting',
            'date_manager': fields.Date.today(),
        })

    def action_schedule_meeting(self):
        """Open calendar to schedule meeting."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'context': {
                'default_name': _('Evaluation Meeting: %s') % self.employee_id.name,
                'default_partner_ids': [
                    self.employee_id.user_partner_id.id,
                    self.manager_id.user_id.partner_id.id if self.manager_id.user_id else False,
                ],
                'default_duration': 1.0,
            },
        }

    def action_complete(self):
        """Mark evaluation as complete."""
        self.ensure_one()
        self.write({
            'state': 'done',
            'date_done': fields.Date.today(),
            'employee_signed': True,
            'employee_signed_date': fields.Datetime.now(),
            'manager_signed': True,
            'manager_signed_date': fields.Datetime.now(),
        })
        # Set employee's next appraisal date based on plan
        if self.plan_id and self.plan_id.interval_type != 'adhoc':
            next_date = fields.Date.today()
            from dateutil.relativedelta import relativedelta
            try:
                next_date += relativedelta(months=self.plan_id.interval_months)
            except Exception:
                pass

    def action_cancel(self):
        """Cancel evaluation."""
        self.write({'state': 'cancelled'})

    # ---- Notifications ----

    def _notify_employee_self_evaluation(self):
        """Send mail activity to employee."""
        for rec in self:
            if rec.employee_user_id:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=rec.employee_user_id.id,
                    note=_('Please complete your self-evaluation.'),
                )

    def _notify_manager_evaluation(self):
        """Send mail activity to manager."""
        for rec in self:
            if rec.manager_id and rec.manager_id.user_id:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=rec.manager_id.user_id.id,
                    note=_('Please complete the manager evaluation for %s.') % rec.employee_id.name,
                )

    # ---- Actions ----

    def action_view_goals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.evaluation.goal',
            'domain': [('evaluation_id', '=', self.id)],
            'name': _('Goals'),
            'view_mode': 'tree,form',
        }

    def action_view_skills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.evaluation.skill',
            'domain': [('evaluation_id', '=', self.id)],
            'name': _('Skills Assessment'),
            'view_mode': 'tree,form',
        }


class HrEvaluationGoal(models.Model):
    _name = 'hr.evaluation.goal'
    _description = 'Evaluation Goal'
    _order = 'sequence'

    evaluation_id = fields.Many2one('hr.evaluation', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, string="Goal")
    goal_type = fields.Selection([
        ('performance', 'Performance Goal'),
        ('development', 'Development Goal'),
        ('behavior', 'Behavioral Goal'),
        ('team', 'Team Goal'),
    ], default='performance')
    weight = fields.Float(default=1.0, string="Weight")
    target_date = fields.Date(string="Target Date")
    progress = fields.Float(string="Progress (%)", default=0.0)
    status = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='on_track')
    self_comment = fields.Text(string="Employee Comment")
    manager_comment = fields.Text(string="Manager Comment")


class HrEvaluationSkill(models.Model):
    _name = 'hr.evaluation.skill'
    _description = 'Evaluation Skill Assessment'

    evaluation_id = fields.Many2one('hr.evaluation', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True, string="Skill")
    skill_type_id = fields.Many2one('hr.skill.type', related='skill_id.skill_type_id')
    required_level = fields.Selection([
        ('0', 'Not Required'),
        ('1', 'Basic'),
        ('2', 'Good'),
        ('3', 'Advanced'),
        ('4', 'Expert'),
    ], default='2')
    current_level_self = fields.Selection([
        ('0', 'None'),
        ('1', 'Basic'),
        ('2', 'Good'),
        ('3', 'Advanced'),
        ('4', 'Expert'),
    ], string="Current Level (Self)")
    current_level_manager = fields.Selection([
        ('0', 'None'),
        ('1', 'Basic'),
        ('2', 'Good'),
        ('3', 'Advanced'),
        ('4', 'Expert'),
    ], string="Current Level (Manager)")
    development_priority = fields.Selection([
        ('none', 'Not Prioritized'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')
