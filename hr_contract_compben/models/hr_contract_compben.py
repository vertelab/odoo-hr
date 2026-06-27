# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrContractCompBen(models.Model):
    _inherit = 'hr.contract'

    gross_salary = fields.Monetary(
        string="Gross Monthly Salary", tracking=True,
        help="Brutton per month")
    net_salary_estimate = fields.Monetary(
        string="Estimated Net Salary",
        compute='_compute_net_salary', store=True)
    total_compensation = fields.Monetary(
        string="Total Compensation",
        compute='_compute_total_compensation', store=True)
    estimated_pension = fields.Monetary(
        string="Estimated Monthly Pension",
        compute='_compute_estimated_pension')

    benefit_ids = fields.One2many('hr.benefit', 'contract_id', string="Benefits")
    salary_sacrifice_ids = fields.One2many('hr.salary.sacrifice', 'contract_id',
                                            string="Salary Sacrifices")

    @api.depends('gross_salary', 'wage')
    def _compute_net_salary(self):
        for rec in self:
            gross = rec.gross_salary or rec.wage or 0
            rec.net_salary_estimate = int(gross * 0.68) if gross else 0

    @api.depends('gross_salary', 'wage', 'benefit_ids.monthly_value',
                 'salary_sacrifice_ids.monthly_amount')
    def _compute_total_compensation(self):
        for rec in self:
            gross = rec.gross_salary or rec.wage or 0
            benefits = sum(rec.benefit_ids.mapped('monthly_value'))
            sacrifices = sum(rec.salary_sacrifice_ids.mapped('monthly_amount'))
            rec.total_compensation = gross + benefits - sacrifices

    @api.depends('gross_salary', 'wage')
    def _compute_estimated_pension(self):
        for rec in self:
            gross = rec.gross_salary or rec.wage or 0
            rec.estimated_pension = round(gross * 0.18) if gross else 0


class HrBenefit(models.Model):
    _name = 'hr.benefit'
    _description = 'Employee Benefit'
    _order = 'sequence'

    contract_id = fields.Many2one('hr.contract', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, string="Benefit")
    benefit_type = fields.Selection([
        ('car', 'Company Car'),
        ('wellness', 'Wellness Allowance'),
        ('phone', 'Phone/Telecom'),
        ('housing', 'Housing'),
        ('meal', 'Meal Vouchers'),
        ('insurance', 'Insurance'),
        ('pension', 'Supplementary Pension'),
        ('childcare', 'Childcare'),
        ('education', 'Education'),
        ('other', 'Other'),
    ], default='other', required=True)
    monthly_value = fields.Monetary(string="Value/month", required=True)
    currency_id = fields.Many2one('res.currency', related='contract_id.currency_id')
    taxable = fields.Boolean(default=True, string="Taxable Benefit")
    description = fields.Text(string="Notes")
    provider = fields.Char(string="Provider")


class HrSalarySacrifice(models.Model):
    _name = 'hr.salary.sacrifice'
    _description = 'Salary Sacrifice'
    _order = 'sequence'

    contract_id = fields.Many2one('hr.contract', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, string="Sacrifice")
    sacrifice_type = fields.Selection([
        ('pension', 'Extra Pension'),
        ('bike', 'Company Bike'),
        ('parking', 'Parking'),
        ('other', 'Other'),
    ], default='pension', required=True)
    monthly_amount = fields.Monetary(string="Monthly Amount", required=True)
    currency_id = fields.Many2one('res.currency', related='contract_id.currency_id')
    gross_impact = fields.Monetary(
        string="Net Pay Impact", compute='_compute_gross_impact')
    description = fields.Text(string="Notes")

    @api.depends('monthly_amount')
    def _compute_gross_impact(self):
        for rec in self:
            rec.gross_impact = int(rec.monthly_amount * 0.68) if rec.monthly_amount else 0
