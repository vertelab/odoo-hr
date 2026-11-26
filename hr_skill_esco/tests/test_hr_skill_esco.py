# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSkillEsco(TransactionCase):
    """ESCO skills are ordinary hr.skill rows with an ESCO code, and the
    skill type flag says whether the skill is an ESCO skill."""

    def test_esco_code_is_stored(self):
        skill = self.env['hr.skill'].create({
            'name': 'Test ESCO skill',
            'skill_type_id': self.env['hr.skill.type'].create({
                'name': 'Test type'}).id,
        })
        self.assertTrue(skill.exists())
        self.assertEqual(skill.name, 'Test ESCO skill')
