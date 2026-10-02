# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Enhetsöversikt — beskrivande, inte rangordnande.

Visar medlemmarnas aktuella beteendevärden tillsammans så att det går att se
vilka stilar som finns representerade i en grupp och vilka som saknas.

Designprincipen gäller: ingen poäng per medlem, ingen sortering på
"passform", ingen utvärdering. Bara en fördelning.
"""

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _key_unit_overview(self, department_id):
        """Aktuella värden per medlem i en enhet.

        Returnerar en lista av dicts för visning. Ingen aggregering till
        en poäng per person.
        """
        employees = self.search([
            ('department_id', '=', department_id),
        ])
        styles = self.env['hr.workstyle.style'].search([])
        rows = []
        for employee in employees:
            latest = employee.workstyle_latest_id
            if not latest:
                continue
            scores = {line.style_id.id: line.score
                      for line in latest.line_ids}
            rows.append({
                'employee_id': employee.id,
                'employee_name': employee.name,
                'job_id': employee.job_id.id,
                'scores': {style.id: scores.get(style.id, 0)
                           for style in styles},
            })
        return rows

    @api.model
    def _key_absent_styles(self, department_id):
        """Stilar som ingen medlem i enheten ligger inom sin zon för.

        Beskrivande: "gruppen har ingen naturlig bärare av S" — inte ett
        omdöme om någon medlem.
        """
        employees = self.search([('department_id', '=', department_id)])
        present = set()
        for employee in employees:
            latest = employee.workstyle_latest_id
            if latest:
                present.update(
                    line.style_id.id for line in latest.line_ids if line.score)
        all_styles = self.env['hr.workstyle.style'].search([])
        return all_styles.filtered(lambda s: s.id not in present)
