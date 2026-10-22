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
    'name': 'HR: Certificates — Restaurant',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Food hygiene and alcohol serving certifications.',
    'category': 'Human Resources',
    'description': '''
HR: Certificates — Restaurant
=============================

    The certifications a restaurant has to hold, on top of
    hr_skills_certificate.

    Industry bridge: a restaurant needs food hygiene and, if it serves
    alcohol, a serving licence held by someone on every shift. An office
    needs neither.

    Included:

        Livsmedelshygien            EG 852/2004, HACCP
        Alkoholservering            Alkohollagen (2010:1622) 3 kap
        Egenkontroll / HACCP        EG 852/2004
        Allergenhantering           EU 1169/2011

    Allergenhantering is its own certification because it is its own legal
    duty: since EU 1169/2011 the information must be available in writing,
    and the person answering the question has to know. It is not covered by
    the general hygiene course.

    The alcohol licence is personal and tied to the establishment: the
    holder must be present or reachable during serving. Modelling it as a
    skill means the roster can be checked against it.

    Features:

        - One skill type for restaurant certifications
        - Four certifications seeded
        - Expiry tracked through Odoo's expiration_status
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_certificate_restaurant',
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
