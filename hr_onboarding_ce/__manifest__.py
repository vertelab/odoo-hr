# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR: Onboarding & Offboarding',
    'version': '18.0.1.0.0',
    'summary': 'Structured onboarding and offboarding with checklists and task delegation.',
    'category': 'Human Resources',
    'description': """
Onboarding & Offboarding
========================

Structured employee lifecycle management:
- Onboarding templates per role/department (IT, sales, manager, finance, etc.)
- Automatic checklists triggered by contract state (signed → onboarding starts)
- Task delegation: IT gets account setup, manager books intro meeting, HR registers insurance
- Timeline with deadlines (day 0, day 7, day 30, day 90)
- Offboarding checklists: return equipment, exit interview, certificate generation
- Dashboard: "3 active onboardings, 2 overdue tasks"

Integrates with:
- hr_contract (triggers on contract start)
- project.task (for checklist items)
- helpdesk (for equipment requests via hr_personal_equipment_helpdesk)
- l10n_se_arbetsgivarintyg (auto-generate employer certificate)
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/',
    'license': 'AGPL-3',
    'depends': ['hr', 'hr_contract', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_onboarding_data.xml',
        'views/hr_onboarding_views.xml',
        'views/hr_onboarding_template_views.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
