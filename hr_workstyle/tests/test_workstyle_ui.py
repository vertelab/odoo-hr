# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Vy-rendering: att vyer faktiskt laddar, inte bara är välformad XML.

XML-validering säger inget om en xpath matchar. `get_views()` tvingar fram
renderingen och fångar brutna xpath-uttryck, saknade fält och felaktiga
inheritance-referenser.
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestWorkstyleViews(TransactionCase):

    def _check(self, model, views):
        """Tvinga fram rendering och verifiera att varje vy har en arch.

        Odoo 18: get_views() returnerar {'views': {'form': {'arch': ...}},
        'models': ...} — inte en 'arch'-nyckel pa toppniva.
        """
        info = self.env[model].get_views(views)
        self.assertIn('views', info)
        for view_type, view in info['views'].items():
            self.assertTrue(
                view.get('arch'),
                "Vyn %s (%s) renderades utan arch" % (model, view_type))

    def test_job_form_renders(self):
        """Fliken Beteendeprofil på hr.job."""
        self._check('hr.job', [(False, 'form')])

    def test_employee_form_renders(self):
        """Fliken Beteendeprofil på hr.employee."""
        self._check('hr.employee', [(False, 'form')])

    def test_applicant_form_renders(self):
        """Fliken Beteendeprofil på hr.applicant."""
        self._check('hr.applicant', [(False, 'form')])

    def test_assessment_form_renders(self):
        self._check('hr.workstyle.assessment', [(False, 'form')])
        self._check('hr.workstyle.assessment', [(False, 'list')])

    def test_style_views_render(self):
        self._check('hr.workstyle.style', [(False, 'form')])
        self._check('hr.workstyle.style', [(False, 'list')])

    def test_trend_form_renders(self):
        self._check('hr.workstyle.trend', [(False, 'form')])

    def test_key_views_render(self):
        self._check('hr.key.analysis.type', [(False, 'form')])
        self._check('hr.key.analysis.type', [(False, 'list')])
        self._check('hr.key.rationale', [(False, 'list')])
        self._check('hr.key.unit.overview', [(False, 'form')])

    def test_no_tree_view_mode_anywhere(self):
        """Odoo 18: view_mode far aldrig innehalla 'tree'."""
        actions = self.env['ir.actions.act_window'].search([
            ('res_model', 'in', [
                'hr.workstyle.style', 'hr.workstyle.assessment',
                'hr.key.analysis.type', 'hr.key.rationale']),
        ])
        for action in actions:
            self.assertNotIn(
                'tree', (action.view_mode or ''),
                "view_mode innehaller 'tree' pa %s" % action.name)

    def test_no_attrs_attribute_anywhere(self):
        """Odoo 18: attrs= ar borttaget och ger ParseError."""
        views = self.env['ir.ui.view'].search([
            ('model', 'in', [
                'hr.job', 'hr.employee', 'hr.applicant',
                'hr.workstyle.style', 'hr.workstyle.assessment',
                'hr.workstyle.trend', 'hr.key.analysis.type',
                'hr.key.rationale', 'hr.key.unit.overview']),
        ])
        for view in views:
            if view.arch:
                self.assertNotIn(
                    'attrs=', view.arch,
                    "attrs= finns kvar i vy %s" % view.name)

    def test_menus_have_parent(self):
        """Menyer maste ha en giltig foralder."""
        menus = self.env['ir.ui.menu'].search([
            ('name', 'in', [
                'Behavioural Profiles', 'Measurements', 'Styles',
                'KEY: Behaviour', 'Analysis Types', 'Rationales',
                'Unit Overview']),
        ])
        self.assertTrue(menus, "Inga menyer hittades")
        top = menus.filtered(lambda m: m.name == 'Behavioural Profiles')
        self.assertTrue(top.parent_id, "Rotmenyn saknar foralder")
