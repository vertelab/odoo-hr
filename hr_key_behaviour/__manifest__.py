# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# https://www.odoo.com/documentation/18.0/reference/module.html

{
    'name': 'HR: Key Behaviour',
    'version': '18.0.1.0.0',
    'summary': 'KEY: Behaviour terminology and analysis types for behavioural profiles.',
    'category': 'Human Resources',
    'description': '''
HR: Key Behaviour
=================

    Leverantörsspecifikt lager ovanpå hr_workstyle för KEY: Behaviour.

    VARFÖR SEPARAT MODUL: leverantörens färger och ordval är specifika för
    en DISC-tradition. Låg de i den generiska modulen skulle en kund med en
    annan leverantör få fel färger från dag ett, och grundmodellen behöva
    ändras för varje ny leverantör. Här ligger de som DATA.

    Features:

        - Färger och terminologi för de fyra stilarna
        - Analystyper: Individ, Roll, 360°, Team
        - Antal feedbackgivare vid 360° (utan att lagra identiteter i poängen)
        - Handledarens validering av mätningen
        - Enhetsöversikt över beteenden i en grupp
        - Rationale-vokabulär för kravrader

    Designprincipen från hr_workstyle gäller oförändrad: modulen beskriver
    beteenden, aldrig personer. Enhetsöversikten är beskrivande och rangordnar
    eller betygsätter inte enskilda medlemmar.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_key_behaviour',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'depends': [
        'hr_workstyle',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_key_behaviour_data.xml',
        'views/hr_key_behaviour_views.xml',
        'views/hr_workstyle_assessment_views.xml',
        'views/hr_job_views.xml',
        'views/menu.xml',
    ],    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
