# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Enhetsöversikt — beskrivande, inte rangordnande.

Visar medlemmarnas aktuella beteendevärden tillsammans så att det går att se
vilka stilar som finns representerade i en grupp och vilka som saknas.

Designprincipen från hr_workstyle gäller: ingen poäng per medlem, ingen
sortering på "passform", ingen utvärdering. Bara en fördelning — och en
markering av vilka stilar ingen i gruppen bär.
"""

from odoo import api, fields, models


class HrKeyUnitOverview(models.TransientModel):
    _name = 'hr.key.unit.overview'
    _description = 'Unit Behavioural Overview'

    department_id = fields.Many2one(
        'hr.department', string='Unit', required=True)
    line_ids = fields.One2many(
        'hr.key.unit.overview.line', 'overview_id', string='Members')
    absent_style_ids = fields.Many2many(
        'hr.workstyle.style', string='Styles with no bearer')

    @api.onchange('department_id')
    def _onchange_department_id(self):
        self.line_ids = [(5, 0, 0)]
        self.absent_style_ids = [(5, 0, 0)]
        if not self.department_id:
            return
        Employee = self.env['hr.employee']
        styles = self.env['hr.workstyle.style'].search([])
        present = set()
        lines = []
        for employee in Employee.search([
                ('department_id', '=', self.department_id.id)]):
            latest = employee.workstyle_latest_id
            if not latest:
                continue
            scores = {line.style_id.id: line.score
                      for line in latest.line_ids}
            present.update(sid for sid, score in scores.items() if score)
            lines.append((0, 0, {
                'employee_id': employee.id,
                'job_id': employee.job_id.id,
                'd_value': scores.get(
                    styles.filtered(lambda s: s.code == 'D').id, 0),
                'i_value': scores.get(
                    styles.filtered(lambda s: s.code == 'I').id, 0),
                's_value': scores.get(
                    styles.filtered(lambda s: s.code == 'S').id, 0),
                'c_value': scores.get(
                    styles.filtered(lambda s: s.code == 'C').id, 0),
            }))
        self.line_ids = lines
        self.absent_style_ids = [
            (6, 0, styles.filtered(lambda s: s.id not in present).ids)]

    @api.model
    def action_open(self):
        """Öppna översikten från menyn."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Unit Behavioural Overview',
            'res_model': 'hr.key.unit.overview',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_department_id': self.env.context.get(
                'default_department_id')},
        }


class HrKeyUnitOverviewLine(models.TransientModel):
    _name = 'hr.key.unit.overview.line'
    _description = 'Unit Behavioural Overview Line'
    _order = 'employee_id'

    overview_id = fields.Many2one(
        'hr.key.unit.overview', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Member')
    job_id = fields.Many2one('hr.job', string='Job Position')
    d_value = fields.Integer(string='D')
    i_value = fields.Integer(string='I')
    s_value = fields.Integer(string='S')
    c_value = fields.Integer(string='C')
