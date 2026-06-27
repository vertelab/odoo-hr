# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models, _


class HrEvaluationPlan(models.Model):
    _name = 'hr.evaluation.plan'
    _description = 'Evaluation Plan'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company')

    # Periodicity
    interval_type = fields.Selection([
        ('probation', 'Probation (5 months)'),
        ('annual', 'Annual'),
        ('biannual', 'Biannual'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
        ('adhoc', 'Ad-hoc'),
    ], required=True, default='annual')
    interval_months = fields.Integer(default=12, help="Months between evaluations")

    # Steps / flow
    step_ids = fields.One2many('hr.evaluation.plan.step', 'plan_id', string="Steps")

    # Participants
    require_self = fields.Boolean(default=True, string="Self-evaluation")
    require_manager = fields.Boolean(default=True, string="Manager")
    require_collaborators = fields.Boolean(default=False, string="Peers")
    require_direct_reports = fields.Boolean(default=False, string="Direct Reports")
    require_skip_level = fields.Boolean(default=False, string="Skip-level Manager")

    # Survey templates
    survey_id = fields.Many2one('survey.survey', string="Evaluation Survey")
    self_evaluation_survey_id = fields.Many2one('survey.survey', string="Self-evaluation Survey")

    # Target: departments, jobs
    department_ids = fields.Many2many('hr.department', string="Departments")
    job_ids = fields.Many2many('hr.job', string="Job Positions")

    # Swedish template type
    template_type = fields.Selection([
        ('medarbetarsamtal', 'Medarbetarsamtal'),
        ('lonesamtal', 'Lönesamtal'),
        ('utvecklingssamtal', 'Utvecklingssamtal'),
        ('provanstallning', 'Provanställning'),
        ('malavstamning', 'Målavstämning'),
        ('custom', 'Custom'),
    ], default='medarbetarsamtal')

    # Description shown to employees
    description = fields.Html(translate=True, help="Instructions shown to the employee")

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)',
         'An evaluation plan with this name already exists for this company.'),
    ]

    def action_create_evaluations(self):
        """Create evaluations for all matching employees."""
        self.ensure_one()
        Evaluation = self.env['hr.evaluation']
        domain = [('active', '=', True)]
        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))
        if self.job_ids:
            domain.append(('job_id', 'in', self.job_ids.ids))
        employees = self.env['hr.employee'].search(domain)
        evaluations = Evaluation
        for emp in employees:
            evaluations += Evaluation.create({
                'employee_id': emp.id,
                'plan_id': self.id,
                'date_planned': fields.Date.today(),
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.evaluation',
            'domain': [('id', 'in', evaluations.ids)],
            'name': _('Created Evaluations'),
            'view_mode': 'tree,form',
        }


class HrEvaluationPlanStep(models.Model):
    _name = 'hr.evaluation.plan.step'
    _description = 'Evaluation Plan Step'
    _order = 'sequence'

    plan_id = fields.Many2one('hr.evaluation.plan', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    step_type = fields.Selection([
        ('self', 'Self-evaluation'),
        ('manager', 'Manager Evaluation'),
        ('peer', 'Peer Feedback'),
        ('direct_report', 'Direct Report Feedback'),
        ('meeting', 'Evaluation Meeting'),
        ('sign', 'Sign-off'),
        ('follow_up', 'Follow-up'),
    ], required=True)
    survey_id = fields.Many2one('survey.survey', string="Survey for this step")
    deadline_days = fields.Integer(default=14, string="Deadline (days from start)")
    required = fields.Boolean(default=True, string="Required step")
    description = fields.Html(translate=True, help="Instructions for this step")
