# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR: Contract Compensation & Benefits',
    'version': '18.0.1.0.0',
    'summary': 'Total compensation view with salary configurator, benefits registry and total reward statement.',
    'category': 'Human Resources',
    'description': 'Compensation & Benefits management for employee contracts.',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/',
    'license': 'AGPL-3',
    'depends': ['hr_contract', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_compben_views.xml',
        'views/hr_benefit_views.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
