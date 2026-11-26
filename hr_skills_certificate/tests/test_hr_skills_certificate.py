# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSkillsCertificate(TransactionCase):
    """A skill type can be flagged as a certification type, and a CV line can
    carry the certificate number, issuer and URL."""

    def test_skill_type_can_be_a_certification_type(self):
        skill_type = self.env['hr.skill.type'].create({
            'name': 'Test certification type',
            'is_certification': True,
        })
        self.assertTrue(skill_type.is_certification)

    def test_cv_line_carries_the_certificate(self):
        employee = self.env['hr.employee'].create({'name': 'Test employee'})
        line = self.env['hr.resume.line'].create({
            'employee_id': employee.id,
            'name': 'Test certificate',
            'date_start': '2026-01-01',
            'certificate_number': 'C-1',
            'certificate_issuer': 'Test issuer',
            'certificate_url': 'https://example.com/cert',
        })
        self.assertEqual(line.certificate_number, 'C-1')
        self.assertEqual(line.certificate_issuer, 'Test issuer')
        self.assertEqual(line.certificate_url, 'https://example.com/cert')
