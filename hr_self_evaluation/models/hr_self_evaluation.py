# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models, _


class HrSelfEvaluation(models.Model):
    _name = 'hr.self.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Self Evaluation'

    evaluation_id = fields.Many2one(
        'hr.evaluation', string="Evaluation",
        required=True, ondelete='cascade',
        help="The parent evaluation this self-evaluation belongs to.")
    employee_id = fields.Many2one(
        'hr.employee', required=True, string="Employee",
        related='evaluation_id.employee_id', store=True)
    manager_id = fields.Many2one(
        'hr.employee', string="Manager",
        related='evaluation_id.manager_id', store=True)
    date = fields.Date(default=fields.Date.today)

    # Reflection fields
    achievements = fields.Text(string="What went well?")
    challenges = fields.Text(string="What was challenging?")
    improvements = fields.Text(string="What can be improved?")
    development_wishes = fields.Text(string="Development wishes")
    support_needed = fields.Text(string="What support do you need?")
    career_goals = fields.Text(string="Career goals (1-3 years)")

    # Self-rating on Likert scale
    performance_self_rating = fields.Selection([
        ('1', '1 - Below Expectations'),
        ('2', '2'),
        ('3', '3 - Meets Expectations'),
        ('4', '4'),
        ('5', '5 - Outstanding'),
    ], string="Performance (self)")

    wellbeing_rating = fields.Selection([
        ('1', '1 - Poor'), ('2', '2'), ('3', '3 - OK'), ('4', '4'), ('5', '5 - Great')
    ], string="Wellbeing / Workload")

    engagement_rating = fields.Selection([
        ('1', '1 - Low'), ('2', '2'), ('3', '3 - OK'), ('4', '4'), ('5', '5 - High')
    ], string="Engagement / Motivation")

    # Survey integration
    survey_response_id = fields.Many2one('survey.user_input', string="Survey Response")

    # Manager comparison (computed after manager evaluation)
    manager_performance_rating = fields.Selection(related='evaluation_id.final_rating',
                                                   string="Performance (manager)")
    rating_comparison = fields.Html(compute='_compute_comparison', string="Comparison")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ], default='draft', tracking=True)

    @api.depends('performance_self_rating', 'manager_performance_rating')
    def _compute_comparison(self):
        for rec in self:
            if rec.performance_self_rating and rec.manager_performance_rating:
                self_val = int(rec.performance_self_rating)
                mgr_val = int(rec.manager_performance_rating)
                diff = mgr_val - self_val
                if diff > 0:
                    rec.rating_comparison = _(
                        '<p>Manager rated <b>%s point(s) higher</b> than your self-assessment.</p>') % diff
                elif diff < 0:
                    rec.rating_comparison = _(
                        '<p>Manager rated <b>%s point(s) lower</b> than your self-assessment.</p>') % abs(diff)
                else:
                    rec.rating_comparison = _('<p>Your self-assessment <b>matches</b> the manager\'s rating.</p>')
            else:
                rec.rating_comparison = ''

    def action_submit(self):
        """Submit self-evaluation and trigger next step in parent evaluation."""
        self.ensure_one()
        self.write({'state': 'submitted'})
        if self.evaluation_id and self.evaluation_id.state == 'self_evaluation':
            self.evaluation_id.action_submit_self()

    def action_review(self):
        """Manager marks as reviewed."""
        self.write({'state': 'reviewed'})
