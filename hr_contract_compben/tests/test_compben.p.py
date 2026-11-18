# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestCompBen(TransactionCase):
    """The benefits hang off the employment record.

    18.0: that record is hr.contract.
    19.0+: hr_contract is gone and the record is hr.version, which
    hr.employee inherits. The test asks the model for the field instead of
    naming a table, so the same test runs on every edition.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # #if VERSION >= "19.0"
        cls.employment = cls.env['hr.version']
        # #else
        cls.employment = cls.env['hr.contract']
        # #endif

    def test_benefit_is_readable_from_the_employment_record(self):
        rec = self.employment.create({'name': 'Test employment'})
        benefit = self.env['hr.benefit'].create({
            'contract_id': rec.id,
            'name': 'Wellness',
            'benefit_type': 'wellness',
            'monthly_value': 400.0,
        })
        self.assertEqual(benefit.contract_id, rec)
        self.assertEqual(benefit.monthly_value, 400.0)
        self.assertIn(benefit, rec.benefit_ids)

    def test_benefits_roll_up_to_the_employment_record(self):
        rec = self.employment.create({
            'name': 'Test employment',
            'gross_salary': 40000.0,
        })
        self.env['hr.benefit'].create({
            'contract_id': rec.id,
            'name': 'Wellness',
            'benefit_type': 'wellness',
            'monthly_value': 400.0,
        })
        self.env['hr.benefit'].create({
            'contract_id': rec.id,
            'name': 'Phone',
            'benefit_type': 'phone',
            'monthly_value': 200.0,
        })
        rec.invalidate_recordset()
        self.assertEqual(rec.total_benefit_value, 600.0)
        self.assertEqual(rec.total_compensation, 40600.0)

    def test_salary_sacrifice_reduces_total_compensation(self):
        rec = self.employment.create({
            'name': 'Test employment',
            'gross_salary': 40000.0,
        })
        self.env['hr.salary.sacrifice'].create({
            'contract_id': rec.id,
            'name': 'Extra pension',
            'sacrifice_type': 'pension',
            'monthly_amount': 2000.0,
        })
        rec.invalidate_recordset()
        self.assertEqual(rec.total_compensation, 38000.0)
