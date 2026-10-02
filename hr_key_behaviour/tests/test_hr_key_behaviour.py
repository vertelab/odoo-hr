# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestKeyBehaviour(TransactionCase):

    def test_seed_sets_local_names_and_colours(self):
        """Utgångsdata sätter leverantörens ordval och färger."""
        Style = self.env['hr.workstyle.style']
        d = Style.search([('code', '=', 'D')])
        i = Style.search([('code', '=', 'I')])
        s = Style.search([('code', '=', 'S')])
        c = Style.search([('code', '=', 'C')])
        self.assertEqual(d.local_name, 'Röd')
        self.assertEqual(i.local_name, 'Gul')
        self.assertEqual(s.local_name, 'Grön')
        self.assertEqual(c.local_name, 'Blå')
        self.assertTrue(d.color)

    def test_vocabulary_is_editable(self):
        """Seeden är utgångspunkt, inte sanning."""
        d = self.env['hr.workstyle.style'].search([('code', '=', 'D')])
        d.local_name = 'Kundens namn'
        d.color = '#123456'
        self.assertEqual(d.local_name, 'Kundens namn')

    def test_analysis_types_seeded(self):
        types = self.env['hr.key.analysis.type'].search([])
        codes = set(types.mapped('code'))
        self.assertEqual(codes, {'individual', 'role', '360', 'team'})

    def test_360_has_feedback_providers(self):
        t = self.env['hr.key.analysis.type'].search([('code', '=', '360')])
        self.assertTrue(t.has_feedback_providers)
        self.assertTrue(t.applies_to_person)

    def test_role_does_not_measure_person(self):
        t = self.env['hr.key.analysis.type'].search([('code', '=', 'role')])
        self.assertFalse(t.applies_to_person)

    def test_team_measures_group(self):
        t = self.env['hr.key.analysis.type'].search([('code', '=', 'team')])
        self.assertTrue(t.measures_group)

    def test_validation_flag(self):
        employee = self.env['hr.employee'].create({'name': 'Test'})
        d = self.env['hr.workstyle.style'].search([('code', '=', 'D')])
        t = self.env['hr.key.analysis.type'].search([('code', '=', 'individual')])
        assessment = self.env['hr.workstyle.assessment'].create({
            'res_model': 'hr.employee', 'res_id': employee.id,
            'analysis_type_id': t.id,
            'line_ids': [(0, 0, {'style_id': d.id, 'score': 5})],
        })
        self.assertFalse(assessment.validated)
        assessment.action_mark_validated()
        self.assertTrue(assessment.validated)
        self.assertTrue(assessment.validation_date)

    def test_360_feedback_count_without_identities(self):
        """Endast antalet lagras — inte feedbackgivarnas identiteter."""
        employee = self.env['hr.employee'].create({'name': 'Test'})
        d = self.env['hr.workstyle.style'].search([('code', '=', 'D')])
        t = self.env['hr.key.analysis.type'].search([('code', '=', '360')])
        assessment = self.env['hr.workstyle.assessment'].create({
            'res_model': 'hr.employee', 'res_id': employee.id,
            'analysis_type_id': t.id, 'feedback_provider_count': 6,
            'line_ids': [(0, 0, {'style_id': d.id, 'score': 5})],
        })
        self.assertEqual(assessment.feedback_provider_count, 6)
        field_names = set(assessment._fields)
        self.assertFalse(
            {'provider_ids', 'feedback_ids'} & field_names,
            "Feedbackgivarnas identiteter ska inte lagras")

    def test_rationale_vocabulary(self):
        rationales = self.env['hr.key.rationale'].search([])
        self.assertTrue(rationales)

    def test_unit_overview_is_descriptive(self):
        """Enhetsöversikten rangordnar eller betygsätter inte."""
        dept = self.env['hr.department'].create({'name': 'Testavdelning'})
        d = self.env['hr.workstyle.style'].search([('code', '=', 'D')])
        for name, score in [('A', 7), ('B', 3)]:
            emp = self.env['hr.employee'].create({
                'name': name, 'department_id': dept.id})
            self.env['hr.workstyle.assessment'].create({
                'res_model': 'hr.employee', 'res_id': emp.id,
                'line_ids': [(0, 0, {'style_id': d.id, 'score': score})],
            })
        overview = self.env['hr.key.unit.overview'].new(
            {'department_id': dept.id})
        overview._onchange_department_id()
        self.assertEqual(len(overview.line_ids), 2)
        # Ingen poäng per medlem som ett aggregerat mått
        forbidden = {'match', 'total', 'score', 'fit', 'rank'}
        for name in overview._fields:
            self.assertFalse(
                set(name.lower().split('_')) & forbidden,
                "Enhetsöversikten ska inte ha fältet %s" % name)
