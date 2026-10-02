# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Mätningar på hr.employee — och de HÄRLEDDA aktuella värdena.

De aktuella värdena är compute-fält, aldrig lagrad sanning. Sanningen är
mätningen (hr.workstyle.assessment). Detta är samma mönster som
hr.employee.skill.log: aktuellt värde = senaste historikposten.
"""

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    workstyle_assessment_ids = fields.One2many(
        'hr.workstyle.assessment', 'res_id',
        string='Behavioural Measurements',
        domain=[('res_model', '=', 'hr.employee')])

    workstyle_assessment_count = fields.Integer(
        string='Measurements',
        compute='_compute_workstyle_assessment_count')

    workstyle_latest_id = fields.Many2one(
        'hr.workstyle.assessment', string='Latest Measurement',
        compute='_compute_workstyle_latest')

    workstyle_d_latest = fields.Integer(
        string='D', compute='_compute_workstyle_latest', store=False)
    workstyle_i_latest = fields.Integer(
        string='I', compute='_compute_workstyle_latest', store=False)
    workstyle_s_latest = fields.Integer(
        string='S', compute='_compute_workstyle_latest', store=False)
    workstyle_c_latest = fields.Integer(
        string='C', compute='_compute_workstyle_latest', store=False)

    workstyle_gap_ids = fields.One2many(
        'hr.workstyle.gap', compute='_compute_workstyle_gap',
        string='Behavioural Gap')

    @api.depends('workstyle_assessment_ids')
    def _compute_workstyle_assessment_count(self):
        for employee in self:
            employee.workstyle_assessment_count = len(
                employee.workstyle_assessment_ids)

    @api.depends('workstyle_assessment_ids',
                 'workstyle_assessment_ids.date',
                 'workstyle_assessment_ids.line_ids.score')
    def _compute_workstyle_latest(self):
        for employee in self:
            latest = employee.workstyle_assessment_ids.sorted(
                key=lambda a: (a.date or fields.Date.today(), a.id),
                reverse=True)[:1]
            employee.workstyle_latest_id = latest
            scores = {}
            if latest:
                scores = {line.style_id.code: line.score
                          for line in latest.line_ids}
            employee.workstyle_d_latest = scores.get('D', 0)
            employee.workstyle_i_latest = scores.get('I', 0)
            employee.workstyle_s_latest = scores.get('S', 0)
            employee.workstyle_c_latest = scores.get('C', 0)

    @api.depends('workstyle_latest_id', 'job_id',
                 'job_id.workstyle_line_ids')
    def _compute_workstyle_gap(self):
        """Gap-rader som virtuella poster (inget skrivs till databasen).

        En computed One2many mot en TransientModel måste tilldelas ett
        recordset — inte kommandon. `.new()` ger virtuella poster som
        försvinner när vyn stängs.
        """
        Gap = self.env['hr.workstyle.gap']
        for employee in self:
            rows = Gap._rows_for('hr.employee', employee.id)
            employee.workstyle_gap_ids = Gap.browse(
                [Gap.new(row).id for row in rows])

    def action_view_workstyle_assessments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Behavioural Measurements',
            'res_model': 'hr.workstyle.assessment',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', 'hr.employee'),
                       ('res_id', '=', self.id)],
            'context': {'default_res_model': 'hr.employee',
                        'default_res_id': self.id},
        }

    def action_open_workstyle_trend(self):
        """Öppna utvecklingsvyn (poäng över tid mot tjänstens zon)."""
        self.ensure_one()
        return self.env['hr.workstyle.trend'].action_open(
            'hr.employee', self.id)
