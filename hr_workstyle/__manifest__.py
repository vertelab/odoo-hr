# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# https://www.odoo.com/documentation/18.0/reference/module.html

{
    'name': 'HR: Workstyle Profile (Beteendeprofil)',
    'version': '18.0.1.0.0',
    'summary': 'Behavioural style profiles for job positions and people (DISC-style).',
    'category': 'Human Resources',
    'description': '''
HR: Workstyle Profile (Beteendeprofil)
======================================

    Beskriver vilka BETEENDEN en tjänst förväntar sig och jämför dem med en
    persons nuvarande beteendeprofil — för både anställda och kandidater.

    Beteende är inte kompetens. `hr_skills` beskriver vad någon KAN; denna
    modul beskriver HUR någon agerar. De två taxonomierna hålls åtskilda.

    Features:

        - Style catalogue (D/I/S/C) with administrable names and colours
        - Behavioural profile on hr.job as a range per style
        - Measurements on hr.employee and hr.applicant, with history
        - Gap analysis: within / below / above the role's expected range
        - Development view over time
        - Copy of measurements when an applicant is hired

    DESIGNPRINCIP: modulen beskriver beteenden, aldrig personer. Den visar
    zoner, staplar och avvikelser — men aldrig en aggregerad
    matchningsprocent, aldrig rangordning av kandidater, aldrig automatisk
    gallring.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_workstyle',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'hr_recruitment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_workstyle_security.xml',
        'data/hr_workstyle_data.xml',
        'views/hr_workstyle_style_views.xml',
        'views/hr_job_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_workstyle_assessment_views.xml',
        'views/hr_workstyle_trend_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
