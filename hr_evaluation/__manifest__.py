# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# https://www.odoo.com/documentation/18.0/reference/module.html

{
    'name': 'HR: Employee Evaluations (Medarbetarsamtal)',
    'version': '18.0.1.0.0',
    'summary': 'Periodic employee evaluations with self-evaluation, goals, and skills assessment.',
    'category': 'Human Resources/Appraisals',
    'description': '''
Employee Evaluations (Medarbetarsamtal)
=======================================

    Periodic employee evaluations (medarbetarsamtal) with:
    - Evaluation plans with configurable steps (self, manager, peers, meeting, sign)
    - Self-evaluation before the meeting
    - Goal management with SMART/OKR support
    - Skills assessment linked to ESCO taxonomy
    - 360-degree feedback
    - Swedish standard templates (medarbetarsamtal, lönesamtal, utvecklingssamtal, provanställning)
    - Integration with systematic work environment (mgmtsystem_sam)
    - Integration with ESCO skills (hr_skill_esco)

    Features:

        - UI Integration: Extends 3 view(s) in the Odoo interface.
        - Extends Odoo: Builds on employee_id, hr.evaluation, hr.evaluation.goal, hr.evaluation.plan.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_evaluation',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'hr_skills',
        'survey',
        'calendar',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_evaluation_plan_views.xml',
        'views/hr_evaluation_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
