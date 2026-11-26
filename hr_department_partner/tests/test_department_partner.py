# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDepartmentPartner(TransactionCase):
    """A department can carry several addresses, and the employee sees the
    department number through the department."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department = cls.env['hr.department'].create({
            'name': 'Test department',
            'department_number': 'D-42',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test address',
            'type': 'hr_department',
        })

    def test_address_hangs_off_the_department(self):
        address = self.env['hr.department.address'].create({
            'name': self.partner.id,
            'department_id': self.department.id,
        })
        self.assertEqual(address.department_id, self.department)
        self.assertIn(address, self.department.address_ids)

    def test_employee_reads_the_department_number(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test employee',
            'department_id': self.department.id,
        })
        self.assertEqual(employee.department_number, 'D-42')
