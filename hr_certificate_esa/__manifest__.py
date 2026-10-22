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
    'name': 'HR: Certificates — Elsäkerhetsverket',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Electrical safety certifications per ESA 2006:1.',
    'category': 'Human Resources',
    'description': '''
HR: Certificates — Elsäkerhetsverket
====================================

    Electrical safety certifications, on top of hr_skills_certificate.

    Industry bridge: an electrician, a property technician and an elevator
    technician all work in installations where ESA 2006:1 applies. An office
    does not. That is why this is a module and not part of the generic one.

    Included:

        Elsäkerhet                  ESA 2006:1
        Arbete i elanläggning       ESA 2006:1, behörighetskrav
        Arbete i hiss               ESA 2006:1, hiss-specifikt tillägg

    The distinction matters in practice: the general electrical safety
    training does not cover work inside an elevator shaft, which is why the
    elevator variant exists as its own certification. An elevator company
    installs both this module and hr_certificate_hiss.

    Features:

        - One skill type for electrical safety certifications
        - Three certifications seeded
        - Expiry tracked through Odoo's expiration_status
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_certificate_esa',
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
