# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Mätningar på hr.applicant — kandidatens nuvarande beteende.

Samma mönster som hr.employee: aktuella värden härleds från senaste
mätningen. Vid anställning KOPIERAS mätningen till den anställde
(se hr_employee_hire i hr_applicant.py vidareutvecklas av
rekryteringsbryggan) — aldrig flyttas, så att GDPR-radering av
kandidatdata inte förstör den anställdes historik.
"""

from odoo import api, fields, models


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    workstyle_assessment_ids = fields.One2many(
        'hr.workstyle.assessment', 'res_id',
        string='Behavioural Measurements',
        domain=[('res_model', '=', 'hr.applicant')])

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
        for applicant in self:
            applicant.workstyle_assessment_count = len(
                applicant.workstyle_assessment_ids)

    @api.depends('workstyle_assessment_ids',
                 'workstyle_assessment_ids.date',
                 'workstyle_assessment_ids.line_ids.score')
    def _compute_workstyle_latest(self):
        for applicant in self:
            latest = applicant.workstyle_assessment_ids.sorted(
                key=lambda a: (a.date or fields.Date.today(), a.id),
                reverse=True)[:1]
            applicant.workstyle_latest_id = latest
            scores = {}
            if latest:
                scores = {line.style_id.code: line.score
                          for line in latest.line_ids}
            applicant.workstyle_d_latest = scores.get('D', 0)
            applicant.workstyle_i_latest = scores.get('I', 0)
            applicant.workstyle_s_latest = scores.get('S', 0)
            applicant.workstyle_c_latest = scores.get('C', 0)

    @api.depends('workstyle_latest_id', 'job_id',
                 'job_id.workstyle_line_ids')
    def _compute_workstyle_gap(self):
        """Gap-rader som virtuella poster (inget skrivs till databasen)."""
        Gap = self.env['hr.workstyle.gap']
        for applicant in self:
            rows = Gap._rows_for('hr.applicant', applicant.id)
            applicant.workstyle_gap_ids = Gap.browse(
                [Gap.new(row).id for row in rows])

    def action_view_workstyle_assessments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Behavioural Measurements',
            'res_model': 'hr.workstyle.assessment',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', 'hr.applicant'),
                       ('res_id', '=', self.id)],
            'context': {'default_res_model': 'hr.applicant',
                        'default_res_id': self.id},
        }

    def action_open_workstyle_trend(self):
        """Öppna utvecklingsvyn (poäng över tid mot tjänstens zon)."""
        self.ensure_one()
        return self.env['hr.workstyle.trend'].action_open(
            'hr.applicant', self.id)

    # ── Överföring vid anställning ─────────────────────────────────────
    #
    # COPY, inte MOVE. Kandidatdata måste kunna raderas enligt GDPR utan
    # att den anställdes utvecklingshistorik förstörs. Därför skapas nya
    # mätningar på den anställde med `copied_from_id` mot originalet.
    #
    # Tyst kopiering — ingen gransknings-wizard. Fyra tal som redan
    # validerats av en handledare behöver ingen granskning. Det håller
    # denna modul okopplad från CV-överföringen (cv-recruitment-bridge),
    # som behöver sitt granskningssteg eftersom AI-parsning är osäker.

    def _copy_workstyle_to_employee(self, employee):
        """Kopiera kandidatens mätningar till en anställd.

        Idempotent: en mätning som redan kopierats kopieras inte igen.
        Returnerar antalet skapade mätningar.
        """
        self.ensure_one()
        Assessment = self.env['hr.workstyle.assessment']
        created = 0
        for assessment in self.workstyle_assessment_ids:
            already = Assessment.search_count([
                ('copied_from_id', '=', assessment.id),
                ('res_model', '=', 'hr.employee'),
                ('res_id', '=', employee.id),
            ])
            if already:
                continue
            Assessment.create({
                'res_model': 'hr.employee',
                'res_id': employee.id,
                'date': assessment.date,
                'assessor_id': assessment.assessor_id.id,
                'source': 'recruitment',
                'note': assessment.note,
                'copied_from_id': assessment.id,
                'line_ids': [(0, 0, {
                    'style_id': line.style_id.id,
                    'score': line.score,
                }) for line in assessment.line_ids],
            })
            created += 1
        return created

    def create_employee_from_applicant(self):
        """Vidareutveckla standardflödet: kopiera beteendemätningen.

        Anropas när en kandidat blir anställd. `action['res_id']` är den
        nya anställdes id (se hr_recruitment.models.hr_candidate).
        Ingen fråga ställs — kopieringen är tyst.
        """
        action = super().create_employee_from_applicant()
        employee_id = action.get('res_id') if isinstance(action, dict) else None
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            for applicant in self:
                if applicant.workstyle_assessment_ids:
                    applicant._copy_workstyle_to_employee(employee)
        return action
