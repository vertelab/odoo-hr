# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Tester för hr_workstyle.

Täcker de beteenden specen kräver, med tonvikt på det som är lätt att
förstöra av misstag: att inget aggregerat mått uppstår, att över-avvikelse
inte blir ett betyg, och att kopiering vid anställning är idempotent.
"""

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestWorkstyle(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Style = cls.env['hr.workstyle.style']
        cls.Line = cls.env['hr.job.workstyle.line']
        cls.Assessment = cls.env['hr.workstyle.assessment']
        cls.Gap = cls.env['hr.workstyle.gap']

        cls.d = cls.Style.search([('code', '=', 'D')])
        cls.i = cls.Style.search([('code', '=', 'I')])
        cls.s = cls.Style.search([('code', '=', 'S')])
        cls.c = cls.Style.search([('code', '=', 'C')])

        # VD-profilen: utåtriktad men förankrande.
        cls.job = cls.env['hr.job'].create({'name': 'VD (test)'})
        for style, mn, mx, imp in [
            (cls.d, 6, 9, 'important'),
            (cls.i, 6, 9, 'important'),
            (cls.s, 5, 8, 'important'),
            (cls.c, 2, 5, 'nice_to_have'),
        ]:
            cls.Line.create({
                'job_id': cls.job.id, 'style_id': style.id,
                'ideal_min': mn, 'ideal_max': mx, 'importance': imp,
            })

    # ── Katalogen ──────────────────────────────────────────────────────

    def test_styles_seeded(self):
        """Fyra stilar finns med rätt kod och ordning."""
        self.assertEqual(len(self.d + self.i + self.s + self.c), 4)
        self.assertEqual(self.d.sequence, 10)
        self.assertEqual(self.c.sequence, 40)

    def test_colour_is_data_not_hardcoded(self):
        """Färg sätts aldrig av den generiska modulen.

        Attend: när leverantörsmodulen (hr_key_behaviour) är installerad
        sätter DEN färger. Det generiska kontraktet är att en ny stil
        utan angiven färg får tom färg — färgen är data, inte logik.
        """
        style = self.Style.create({'name': 'Neutral', 'code': 'N'})
        self.assertFalse(style.color)
        self.assertFalse(style.local_name)

    def test_colour_is_editable(self):
        self.c.color = '#0000FF'
        self.assertEqual(self.c.color, '#0000FF')

    def test_scale_defaults(self):
        self.assertEqual(self.d.scale_min, 1)
        self.assertEqual(self.d.scale_max, 10)

    def test_scale_must_be_ordered(self):
        with self.assertRaises(ValidationError):
            self.d.write({'scale_min': 10, 'scale_max': 1})

    def test_fifth_style_usable(self):
        """En femte stil kan användas i krav och mätningar."""
        extra = self.Style.create({'name': 'Extra', 'code': 'X'})
        job = self.env['hr.job'].create({'name': 'Extra stil'})
        self.Line.create({
            'job_id': job.id, 'style_id': extra.id,
            'ideal_min': 1, 'ideal_max': 5,
        })
        self.assertIn(extra, job.workstyle_line_ids.style_id)

    # ── Kravprofilen ───────────────────────────────────────────────────

    def test_range_rejected_when_inverted(self):
        job = self.env['hr.job'].create({'name': 'Inverterad'})
        with self.assertRaises(ValidationError):
            self.Line.create({
                'job_id': job.id, 'style_id': self.c.id,
                'ideal_min': 8, 'ideal_max': 2,
            })

    def test_upper_bound_is_mandatory(self):
        """Utan övre gräns blir avvikelsen uppåt osynlig.

        Inga defaults finns på ideal_max — annars skulle required=True
        aldrig utlösas och kravet tyst upphöra att gälla.
        """
        job = self.env['hr.job'].create({'name': 'Utan övre gräns'})
        with self.assertRaises(Exception):
            self.Line.create({
                'job_id': job.id, 'style_id': self.c.id,
                'ideal_min': 5,
            })

    def test_one_line_per_style(self):
        job = self.env['hr.job'].create({'name': 'Dubblett'})
        self.Line.create({
            'job_id': job.id, 'style_id': self.d.id,
            'ideal_min': 1, 'ideal_max': 2,
        })
        with self.assertRaises(Exception):
            self.Line.create({
                'job_id': job.id, 'style_id': self.d.id,
                'ideal_min': 3, 'ideal_max': 4,
            })

    def test_range_must_fit_scale(self):
        job = self.env['hr.job'].create({'name': 'Utanför skala'})
        with self.assertRaises(ValidationError):
            self.Line.create({
                'job_id': job.id, 'style_id': self.c.id,
                'ideal_min': 1, 'ideal_max': 99,
            })

    def test_rationale_optional(self):
        job = self.env['hr.job'].create({'name': 'Utan rationale'})
        line = self.Line.create({
            'job_id': job.id, 'style_id': self.c.id,
            'ideal_min': 1, 'ideal_max': 5,
        })
        self.assertFalse(line.rationale)

    # ── Mätningen ──────────────────────────────────────────────────────

    def _measure(self, employee, scores, date=None):
        vals = {
            'res_model': 'hr.employee', 'res_id': employee.id,
            'line_ids': [(0, 0, {'style_id': st.id, 'score': sc})
                         for st, sc in scores],
        }
        if date:
            vals['date'] = date
        return self.Assessment.create(vals)

    def test_measurement_on_employee(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test', 'job_id': self.job.id})
        assessment = self._measure(employee, [(self.d, 7)])
        self.assertEqual(assessment.res_model, 'hr.employee')
        self.assertEqual(assessment.res_id, employee.id)

    def test_score_outside_scale_rejected(self):
        employee = self.env['hr.employee'].create({'name': 'Test'})
        with self.assertRaises(ValidationError):
            self._measure(employee, [(self.d, 99)])

    def test_rank_identifies_strongest(self):
        employee = self.env['hr.employee'].create({'name': 'Test'})
        assessment = self._measure(employee, [
            (self.d, 7), (self.i, 3), (self.s, 7), (self.c, 8)])
        ranked = assessment.line_ids.sorted('rank')
        self.assertEqual(ranked[0].style_id, self.c)
        self.assertEqual(ranked[0].rank, 1)
        self.assertEqual(ranked[-1].style_id, self.i)

    def test_latest_derived_not_stored(self):
        """Aktuella värden följer senaste mätningen, inte en egen sanning."""
        employee = self.env['hr.employee'].create({
            'name': 'Test', 'job_id': self.job.id})
        self._measure(employee, [(self.d, 3)], date='2024-01-01')
        employee.invalidate_recordset()
        self.assertEqual(employee.workstyle_d_latest, 3)
        self._measure(employee, [(self.d, 9)], date='2025-01-01')
        employee.invalidate_recordset()
        self.assertEqual(employee.workstyle_d_latest, 9)
        self.assertEqual(employee.workstyle_assessment_count, 2)

    def test_older_measurement_not_overwritten(self):
        employee = self.env['hr.employee'].create({'name': 'Test'})
        first = self._measure(employee, [(self.d, 3)], date='2024-01-01')
        self._measure(employee, [(self.d, 9)], date='2025-01-01')
        self.assertEqual(first.line_ids.score, 3)

    def test_no_measurement_no_values(self):
        employee = self.env['hr.employee'].create({'name': 'Test'})
        employee.invalidate_recordset()
        self.assertFalse(employee.workstyle_latest_id)
        self.assertFalse(employee.workstyle_gap_ids)

    # ── Gap-analysen ───────────────────────────────────────────────────

    def test_classify_is_symmetric(self):
        self.assertEqual(self.Gap._classify(3, 6, 9), 'under_zone')
        self.assertEqual(self.Gap._classify(7, 6, 9), 'within')
        self.assertEqual(self.Gap._classify(8, 2, 5), 'over_zone')
        self.assertEqual(self.Gap._classify(0, 6, 9), 'unmeasured')

    def test_gap_three_states(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test', 'job_id': self.job.id})
        self._measure(employee, [
            (self.d, 7), (self.i, 3), (self.s, 7), (self.c, 8)])
        employee.invalidate_recordset()
        by_code = {g.style_id.code: g.deviation
                   for g in employee.workstyle_gap_ids}
        self.assertEqual(by_code['D'], 'within')
        self.assertEqual(by_code['I'], 'under_zone')
        self.assertEqual(by_code['S'], 'within')
        self.assertEqual(by_code['C'], 'over_zone')

    def test_unmeasured_style_is_not_a_gap(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test', 'job_id': self.job.id})
        self._measure(employee, [(self.d, 7)])
        employee.invalidate_recordset()
        by_code = {g.style_id.code: g.deviation
                   for g in employee.workstyle_gap_ids}
        self.assertEqual(by_code['I'], 'unmeasured')
        self.assertEqual(by_code['D'], 'within')

    def test_no_job_profile_no_gap(self):
        job = self.env['hr.job'].create({'name': 'Utan profil'})
        employee = self.env['hr.employee'].create({
            'name': 'Test', 'job_id': job.id})
        self._measure(employee, [(self.d, 7)])
        employee.invalidate_recordset()
        self.assertFalse(employee.workstyle_gap_ids)

    def test_no_aggregated_score_exists(self):
        """Designprincipen: ingen matchningspoäng, ingen procentsats.

        Tokeniserar fältnamnet på '_' så att 'ratio' inte matchar
        mitten av 'rationale' — rationale är ett legitimt fält (motivet
        för ett krav), inte ett aggregerat mått.
        """
        forbidden = {'match', 'total', 'percent', 'ratio', 'fit',
                     'overall', 'aggregate'}
        for model in ('hr.workstyle.gap', 'hr.workstyle.assessment',
                      'hr.workstyle.assessment.line'):
            fields = self.env[model]._fields
            for name in fields:
                tokens = set(name.lower().split('_'))
                self.assertFalse(
                    tokens & forbidden,
                    "Förbjudet aggregerat fält %s på %s" % (name, model))

    def test_gap_rows_are_virtual(self):
        """Gap-raderna skrivs inte till databasen."""
        employee = self.env['hr.employee'].create({
            'name': 'Test', 'job_id': self.job.id})
        self._measure(employee, [(self.d, 7)])
        employee.invalidate_recordset()
        self.assertTrue(employee.workstyle_gap_ids)
        self.assertFalse(
            self.env['hr.workstyle.gap'].search([
                ('res_model', '=', 'hr.employee'),
                ('res_id', '=', employee.id)]),
            "Gap-rader ska vara virtuella, inte lagrade")


@tagged('post_install', '-at_install')
class TestWorkstyleHire(TransactionCase):
    """Överföring vid anställning: COPY, inte MOVE."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.d = cls.env['hr.workstyle.style'].search([('code', '=', 'D')])

    def _applicant_with_measurement(self):
        partner = self.env['res.partner'].create({'name': 'Kandidat'})
        candidate = self.env['hr.candidate'].create({
            'partner_name': 'Kandidat', 'partner_id': partner.id})
        applicant = self.env['hr.applicant'].create({
            'candidate_id': candidate.id, 'partner_name': 'Kandidat'})
        assessment = self.env['hr.workstyle.assessment'].create({
            'res_model': 'hr.applicant', 'res_id': applicant.id,
            'source': 'recruitment',
            'line_ids': [(0, 0, {'style_id': self.d.id, 'score': 6})],
        })
        return applicant, assessment

    def test_copy_creates_new_measurement(self):
        applicant, assessment = self._applicant_with_measurement()
        employee = self.env['hr.employee'].create({'name': 'Kandidat'})
        created = applicant._copy_workstyle_to_employee(employee)
        self.assertEqual(created, 1)
        copied = self.env['hr.workstyle.assessment'].search([
            ('res_model', '=', 'hr.employee'), ('res_id', '=', employee.id)])
        self.assertEqual(len(copied), 1)
        self.assertEqual(copied.copied_from_id, assessment)

    def test_copy_is_not_a_move(self):
        applicant, assessment = self._applicant_with_measurement()
        employee = self.env['hr.employee'].create({'name': 'Kandidat'})
        applicant._copy_workstyle_to_employee(employee)
        self.assertTrue(assessment.exists())
        self.assertEqual(assessment.res_model, 'hr.applicant')

    def test_copy_preserves_scores(self):
        applicant, assessment = self._applicant_with_measurement()
        employee = self.env['hr.employee'].create({'name': 'Kandidat'})
        applicant._copy_workstyle_to_employee(employee)
        copied = self.env['hr.workstyle.assessment'].search([
            ('copied_from_id', '=', assessment.id)])
        self.assertEqual(copied.line_ids.score, 6)
        self.assertEqual(copied.date, assessment.date)

    def test_copy_is_idempotent(self):
        applicant, assessment = self._applicant_with_measurement()
        employee = self.env['hr.employee'].create({'name': 'Kandidat'})
        applicant._copy_workstyle_to_employee(employee)
        again = applicant._copy_workstyle_to_employee(employee)
        self.assertEqual(again, 0)
        copied = self.env['hr.workstyle.assessment'].search([
            ('res_model', '=', 'hr.employee'), ('res_id', '=', employee.id)])
        self.assertEqual(len(copied), 1)

    def test_no_measurement_no_copy(self):
        partner = self.env['res.partner'].create({'name': 'Tom'})
        candidate = self.env['hr.candidate'].create({
            'partner_name': 'Tom', 'partner_id': partner.id})
        applicant = self.env['hr.applicant'].create({
            'candidate_id': candidate.id, 'partner_name': 'Tom'})
        employee = self.env['hr.employee'].create({'name': 'Tom'})
        self.assertEqual(applicant._copy_workstyle_to_employee(employee), 0)

    def test_deleting_applicant_data_keeps_employee_copy(self):
        """GDPR: kandidatens radering får inte förstöra anställdas historik."""
        applicant, assessment = self._applicant_with_measurement()
        employee = self.env['hr.employee'].create({'name': 'Kandidat'})
        applicant._copy_workstyle_to_employee(employee)
        copied = self.env['hr.workstyle.assessment'].search([
            ('copied_from_id', '=', assessment.id)])
        assessment.unlink()
        self.assertTrue(copied.exists())
        self.assertFalse(copied.copied_from_id)
        self.assertEqual(copied.line_ids.score, 6)
