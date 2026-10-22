# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'HR: Certificates — Arbetsmiljöverket',
    'version': '18.0.1.0.2',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Work environment certifications: hot work, fall protection, safety.',
    'category': 'Human Resources',
    'description': '''
HR: Certificates — Arbetsmiljöverket
====================================

    The certifications Swedish employers need to satisfy Arbetsmiljöverket.

    Industry bridge: it adds skill types and certifications as DATA, on top
    of the generic hr_skills_certificate. A metal shop, a construction firm
    and an elevator company all need these; an office does not. That is why
    they live here and not in the generic module.

    Included:

        Heta arbeten            AFS 2006:4
        Fallskydd / Höjdarbete  AFS 2001:1
        Säkerhetsutbildning     AFS 2001:1
        Tunga lyft              AFS 2023:1
        OSA — Organisatorisk
        och social arbetsmiljö  AFS 2023:10

    The validity periods are the ones the training schemes use in practice.
    They are noted per certification in the data file so a customer can see
    where the number came from.

    It does not model the laws themselves. Which paragraphs apply, and what
    they require, is a legal question — see the law requirement proposal for
    odoo-knowledge. This module only says which certifications exist.

    Features:

        - One skill type for work environment certifications
        - Five certifications seeded
        - Expiry tracked through Odoo's expiration_status
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_certificate_arbetsmiljo',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    'depends': [
        'hr_skills_certificate',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/skill_data.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
