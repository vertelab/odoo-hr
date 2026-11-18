# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR: Contract Compensation & Benefits',
    'version': '1.0.0',
    'summary': 'Total compensation view with salary configurator, benefits registry and total reward statement.',
    'description': '''
Contract Compensation & Benefits
================================

    Total compensation view with salary configurator, benefits registry and total reward statement.

    Features:

        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on hr.benefit, hr.contract, hr.salary.sacrifice.
    ''',
    'category': 'Human Resources',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_contract_compben',
    'license': 'AGPL-3',
    # #if VERSION >= "19.0"
    # hr_contract was removed in 19.0 and 20.0: employment is hr.version, and
    # hr.employee inherits it. Nothing to depend on beyond hr.
    'depends': ['hr'],
    # #else
    'depends': ['hr_contract', 'hr'],
    # #endif
    'data': [
        # #if VERSION >= "20.0"
        'security/ir.access.csv',
        # #else
        'security/ir.model.access.csv',
        # #endif
        'views/hr_contract_compben_views.xml',
        'views/hr_benefit_views.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
