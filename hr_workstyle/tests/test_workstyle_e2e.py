# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""End-to-end: VD-profilen från rekrytering till utveckling över tid.

Följer uppgift 9.4-9.6: skapa jobb med VD-profil, mät en kandidat, anställ,
följ utvecklingen över tre mätningar.
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestWorkstyleE2E(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Style = cls.env['hr.workstyle.style']
        cls.d = Style.search([('code', '=', 'D')])
        cls.i = Style.search([('code', '=', 'I')])
        cls.s = Style.search([('code', '=', 'S')])
        cls.c = Style.search([('code', '=', 'C')])

        # "Utåtriktad VD som samtidigt är duktig på att förankra beslut
        #  innan de implementeras."
        cls.job = cls.env['hr.job'].create({'name': 'VD'})
        for style, mn, mx, imp, rat in [
            (cls.d, 6, 9, 'important', 'utåtriktad, driver beslut'),
            (cls.i, 6, 9, 'important', 'utåtriktad, kommunicerar vision'),
            (cls.s, 5, 8, 'important', 'förankrar — lyssnar in'),
            (cls.c, 2, 5, 'nice_to_have', 'ej bromskloss'),
        ]:
            cls.env['hr.job.workstyle.line'].create({
                'job_id': cls.job.id, 'style_id': style.id,
                'ideal_min': mn, 'ideal_max': mx,
                'importance': imp, 'rationale': rat,
            })

    def _measure(self, res_model, res_id, scores, date=None):
        vals = {
            'res_model': res_model, 'res_id': res_id,
            'line_ids': [(0, 0, {'style_id': st.id, 'score': sc})
                         for st, sc in scores],
        }
        if date:
            vals['date'] = date
        return self.env['hr.workstyle.assessment'].create(vals)

    def test_full_flow(self):
        # 1. Kandidat mäts mot VD-profilen.
        partner = self.env['res.partner'].create({'name': 'Kandidat'})
        candidate = self.env['hr.candidate'].create({
            'partner_name': 'Kandidat', 'partner_id': partner.id})
        applicant = self.env['hr.applicant'].create({
            'candidate_id': candidate.id, 'partner_name': 'Kandidat',
            'job_id': self.job.id,
        })
        self._measure('hr.applicant', applicant.id, [
            (self.d, 7), (self.i, 3), (self.s, 7), (self.c, 8)],
            date='2025-01-15')
        applicant.invalidate_recordset()

        by_code = {g.style_id.code: g.deviation
                   for g in applicant.workstyle_gap_ids}
        self.assertEqual(by_code['D'], 'within')
        self.assertEqual(by_code['I'], 'under_zone')   # kommunikativa sidan
        self.assertEqual(by_code['S'], 'within')
        self.assertEqual(by_code['C'], 'over_zone')    # inte en brist

        # 2. Anställning: mätningen kopieras.
        employee = self.env['hr.employee'].create({
            'name': 'Kandidat', 'job_id': self.job.id})
        applicant._copy_workstyle_to_employee(employee)
        employee.invalidate_recordset()
        self.assertEqual(employee.workstyle_assessment_count, 1)
        self.assertEqual(employee.workstyle_i_latest, 3)
        # Kopian behåller rekryteringsmätningens datum.
        copied = self.env['hr.workstyle.assessment'].search([
            ('res_model', '=', 'hr.employee'), ('res_id', '=', employee.id)])
        self.assertEqual(str(copied.date), '2025-01-15')

        # 3. Utveckling över tid: I går 3 -> 5 -> 7.
        #    Kopian behåller rekryteringsmätningens datum (2025-01-15),
        #    så utvecklingsmätningarna läggs därefter.
        self._measure('hr.employee', employee.id, [(self.i, 5)],
                      date='2026-03-01')
        employee.invalidate_recordset()
        self.assertEqual(employee.workstyle_i_latest, 5)
        self._measure('hr.employee', employee.id, [(self.i, 7)],
                      date='2026-09-01')
        employee.invalidate_recordset()
        self.assertEqual(employee.workstyle_i_latest, 7)
        self.assertEqual(employee.workstyle_assessment_count, 3)

        by_code = {g.style_id.code: g.deviation
                   for g in employee.workstyle_gap_ids}
        self.assertEqual(by_code['I'], 'within', "I ska nå målzonen 6-9")

        # 4. Ingen aggregerad poäng någonstans i kedjan.
        for model in ('hr.workstyle.gap', 'hr.workstyle.assessment',
                      'hr.employee', 'hr.applicant'):
            for name in self.env[model]._fields:
                tokens = set(name.lower().split('_'))
                self.assertFalse(
                    tokens & {'match', 'total', 'percent', 'fit', 'rank'},
                    "Aggregerat fält %s på %s" % (name, model))

    def test_development_view_over_measurements(self):
        """Utvecklingsvyn visar poäng över tid med zonen som referens."""
        employee = self.env['hr.employee'].create({
            'name': 'Utveckling', 'job_id': self.job.id})
        self._measure('hr.employee', employee.id, [(self.i, 3)],
                      date='2026-01-01')
        self._measure('hr.employee', employee.id, [(self.i, 5)],
                      date='2026-06-01')
        self._measure('hr.employee', employee.id, [(self.i, 7)],
                      date='2026-12-01')
        trend = self.env['hr.workstyle.trend'].create({
            'res_model': 'hr.employee', 'res_id': employee.id})
        trend._build_lines()
        i_lines = trend.line_ids.filtered(
            lambda l: l.style_id == self.i).sorted('date')
        self.assertEqual([l.score for l in i_lines], [3, 5, 7])
        # Zonen följer med som referens.
        self.assertEqual(i_lines[0].zone_min, 6)
        self.assertEqual(i_lines[0].zone_max, 9)
