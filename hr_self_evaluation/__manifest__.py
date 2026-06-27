# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR: Self Evaluation',
    'version': '18.0.1.0.0',
    'summary': 'Employee self-evaluation (självskattning) before manager evaluation.',
    'category': 'Human Resources/Appraisals',
    'description': """
Self Evaluation for Employees
=============================

Adds a structured self-evaluation form for employees to complete 
before their manager evaluation meeting. Features:

- Reflection fields: achievements, challenges, improvements, career goals
- Likert-scale self-rating on performance, wellbeing, engagement
- Comparison view: self vs manager ratings side by side
- Optional anonymous team surveys for work environment

Built as a companion module to hr_evaluation.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/',
    'license': 'AGPL-3',
    'depends': ['hr_evaluation'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_self_evaluation_views.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
