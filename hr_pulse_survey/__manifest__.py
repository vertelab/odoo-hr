# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-hr/hr_pulse_survey',
    'name': 'HR: Pulse Survey',
    'version': '18.0.1.0.0',
    'summary': 'Recurring pulse surveys with automated alarms and trend analysis.',
    'description': '''
Pulse Survey
============

    Recurring pulse surveys with automated alarms and trend analysis.

    Features:

        - UI Integration: Extends 1 view(s) in the Odoo interface.
        - Extends Odoo: Builds on hr.pulse.survey, mail.thread, survey.user_input.
    ''',
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
