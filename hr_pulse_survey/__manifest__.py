# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR: Pulse Survey',
    'version': '18.0.1.0.0',
    'summary': 'Recurring pulse surveys with automated alarms and trend analysis.',
    'category': 'Human Resources',
    'depends': ['hr', 'survey', 'hr_evaluation'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_pulse_survey_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
