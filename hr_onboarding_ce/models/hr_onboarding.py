# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import api, fields, models, _


class HrOnboardingTemplate(models.Model):
    _name = 'hr.onboarding.template'
    _description = 'Onboarding Template'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    department_ids = fields.Many2many('hr.department', string="Departments")
    job_ids = fields.Many2many('hr.job', string="Job Positions")
    step_ids = fields.One2many('hr.onboarding.template.step', 'template_id',
                                string="Steps")

    def action_generate_tasks(self, contract):
        """Generate project tasks from template for a new employee."""
        project = self.env['project.project'].search(
            [('name', 'ilike', 'Onboarding')], limit=1)
        if not project:
            project = self.env['project.project'].create({
                'name': 'Onboarding',
                'partner_id': contract.employee_id.company_id.partner_id.id,
            })
        tasks = self.env['project.task']
        for step in self.step_ids:
            task = self.env['project.task'].create({
                'name': step.name,
                'project_id': project.id,
                'user_id': step.default_user_id.id,
                'date_deadline': date.today() + timedelta(days=step.deadline_days),
                'description': step.description,
            })
            tasks += task
        return tasks


class HrOnboardingTemplateStep(models.Model):
    _name = 'hr.onboarding.template.step'
    _description = 'Onboarding Template Step'
    _order = 'sequence'

    template_id = fields.Many2one('hr.onboarding.template', required=True,
                                   ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    deadline_days = fields.Integer(default=7, string="Days after start")
    default_user_id = fields.Many2one('res.users', string="Default Assignee")
    responsible_role = fields.Selection([
        ('hr', 'HR'),
        ('it', 'IT'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
        ('finance', 'Finance'),
    ], default='hr', string="Responsible Role")
    description = fields.Html(translate=True, string="Instructions")
    required = fields.Boolean(default=True)


class HrOnboarding(models.Model):
    _name = 'hr.onboarding'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Onboarding'

    name = fields.Char(string="Reference", compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', required=True, string="Employee")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    template_id = fields.Many2one('hr.onboarding.template', string="Template")
    task_ids = fields.One2many('project.task', 'onboarding_id', string="Tasks")
    date_start = fields.Date(string="Start Date", default=fields.Date.today)
    date_deadline = fields.Date(string="Target Completion")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    progress = fields.Float(compute='_compute_progress', string="Progress (%)")
    overdue = fields.Boolean(compute='_compute_progress')

    @api.depends('task_ids')
    def _compute_progress(self):
        for rec in self:
            total = len(rec.task_ids)
            if total:
                done = len(rec.task_ids.filtered(lambda t: t.stage_id and t.stage_id.fold))
                rec.progress = (done / total) * 100
                rec.overdue = any(t.date_deadline and t.date_deadline < date.today()
                                  and not (t.stage_id and t.stage_id.fold)
                                  for t in rec.task_ids)
            else:
                rec.progress = 0
                rec.overdue = False

    @api.depends('employee_id', 'date_start')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.employee_id.name} — Onboarding {rec.date_start or ''}"

    def action_start(self):
        self.ensure_one()
        if self.state != 'draft':
            return
        if self.template_id:
            tasks = self.template_id.action_generate_tasks(self.contract_id)
            self.write({'task_ids': [(6, 0, tasks.ids)]})
        self.write({'state': 'active'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class HrOffboarding(models.Model):
    _name = 'hr.offboarding'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Offboarding'

    employee_id = fields.Many2one('hr.employee', required=True, string="Employee")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    reason = fields.Selection([
        ('resignation', 'Resignation'),
        ('termination', 'Termination'),
        ('retirement', 'Retirement'),
        ('end_contract', 'End of Contract'),
        ('other', 'Other'),
    ], default='resignation', required=True)
    task_ids = fields.One2many('project.task', 'offboarding_id', string="Tasks")
    date_start = fields.Date(default=fields.Date.today)
    last_working_day = fields.Date(required=True)
    exit_interview_date = fields.Date()
    exit_interview_notes = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], default='draft', tracking=True)
    progress = fields.Float(compute='_compute_progress', string="Progress (%)")

    @api.depends('task_ids')
    def _compute_progress(self):
        for rec in self:
            total = len(rec.task_ids)
            if total:
                done = len(rec.task_ids.filtered(lambda t: t.stage_id and t.stage_id.fold))
                rec.progress = (done / total) * 100
            else:
                rec.progress = 0

    name = fields.Char(compute='_compute_name', store=True)

    @api.depends('employee_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.employee_id.name} — Offboarding"

    def action_start(self):
        self.ensure_one()
        if self.task_ids:
            return
        # Default offboarding tasks
        default_tasks = [
            (_('Return equipment'), 'it', 0),
            (_('Exit interview'), 'hr', 5),
            (_('Revoke system access'), 'it', 0),
            (_('Generate employer certificate'), 'hr', 3),
            (_('Knowledge transfer'), 'manager', 5),
            (_('Update payroll'), 'finance', 1),
        ]
        project = self.env['project.project'].search(
            [('name', 'ilike', 'Offboarding')], limit=1)
        if not project:
            project = self.env['project.project'].create({
                'name': 'Offboarding',
            })
        for task_name, role, days in default_tasks:
            self.env['project.task'].create({
                'name': task_name,
                'project_id': project.id,
                'offboarding_id': self.id,
                'date_deadline': self.last_working_day + timedelta(days=days),
            })
        self.write({'state': 'active'})

    def action_complete(self):
        self.write({'state': 'completed'})
