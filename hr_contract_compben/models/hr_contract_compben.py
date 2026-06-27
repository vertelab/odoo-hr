# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContractCompBen(models.Model):
    _inherit = 'hr.contract'

    # ---- Salary Configurator ----
    gross_salary = fields.Monetary(
        string="Gross Monthly Salary", currency_field='currency_id',
        tracking=True, help="Bruttolön per månad")
    net_salary_estimate = fields.Monetary(
        string="Estimated Net Salary", currency_field='currency_id',
        compute='_compute_net_salary', store=True)
    salary_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # ---- Benefits ----
    benefit_ids = fields.One2many('hr.benefit', 'contract_id', string="Benefits")
    total_benefit_value = fields.Monetary(
        string="Total Benefit Value", currency_field='currency_id',
        compute='_compute_total_compensation', store=True)
    total_compensation = fields.Monetary(
        string="Total Compensation", currency_field='currency_id',
        compute='_compute_total_compensation', store=True,
        help="Salary + all benefits")

    # ---- Salary Sacrifice ----
    salary_sacrifice_ids = fields.One2many('hr.salary.sacrifice', 'contract_id',
                                            string="Salary Sacrifices")
    total_sacrifice = fields.Monetary(
        string="Total Sacrifice", currency_field='currency_id',
        compute='_compute_total_compensation', store=True)

    # ---- Pension Forecast ----
    estimated_pension = fields.Monetary(
        string="Estimated Monthly Pension", currency_field='currency_id',
        compute='_compute_estimated_pension')

    @api.depends('gross_salary', 'wage')
    def _compute_net_salary(self):
        """Rough estimate using Swedish tax table integration.
        More precise calculation requires l10n_se_hr_payroll."""
        for rec in self:
            gross = rec.gross_salary or rec.wage
            if gross and gross > 0:
                # Rough Swedish tax estimate: ~32% kommunalskatt for median income
                # Full calculation should use l10n_se_payroll_taxtable
                rec.net_salary_estimate = gross * 0.68
            else:
                rec.net_salary_estimate = 0

    @api.depends('gross_salary', 'wage', 'benefit_ids.monthly_value',
                 'salary_sacrifice_ids.monthly_amount')
    def _compute_total_compensation(self):
        for rec in self:
            gross = rec.gross_salary or rec.wage or 0
            benefits = sum(rec.benefit_ids.mapped('monthly_value'))
            sacrifices = sum(rec.salary_sacrifice_ids.mapped('monthly_amount'))
            rec.total_benefit_value = benefits
            rec.total_sacrifice = sacrifices
            rec.total_compensation = gross + benefits - sacrifices

    @api.depends('gross_salary', 'wage')
    def _compute_estimated_pension(self):
        for rec in self:
            gross = rec.gross_salary or rec.wage or 0
            # Rough estimate: ~18% of salary up to 7.5 IBB + ~30% above
            # ITP1: 4.5% up to ~46k, 30% above
            rec.estimated_pension = round(gross * 0.18)


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
    monthly_value = fields.Monetary(
        string="Value/month", currency_field='currency_id', required=True)
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
    monthly_amount = fields.Monetary(
        string="Monthly Amount", currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', related='contract_id.currency_id')
    gross_impact = fields.Monetary(
        string="Net Pay Impact", currency_field='currency_id', compute='_compute_gross_impact')
    description = fields.Text(string="Notes")

    @api.depends('monthly_amount')
    def _compute_gross_impact(self):
        """Rough estimate of net pay impact after tax savings."""
        for rec in self:
            rec.gross_impact = rec.monthly_amount * 0.68  # rough after-tax
