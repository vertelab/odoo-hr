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
    'name': 'HR: Certificates — Hiss',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Elevator authorisation and inspection certifications.',
    'category': 'Human Resources',
    'description': '''
HR: Certificates — Hiss
=======================

    The certifications that make an elevator technician allowed to work on
    elevators at all.

    Industry bridge: this is the one that distinguishes an elevator company
    from every other field service company. A plumber does not need
    hissinstallation; an elevator technician cannot work without it.

    Included:

        Hissinstallation (auktorisation)   BFS 2011:12
        Hissbesiktning                     BFS 2011:12
        Hisservice — felsökning            BFS 2011:12

    The auktorisation is held by the company, not the individual, but the
    individual technician must be documented as competent under it. That is
    why it is modelled as a skill: the company's authorisation is only as
    good as the people it sends.

    No fixed expiry in the data: the auktorisation follows the company's
    scheme, and the certificate number from hr_skills_certificate is what
    the inspection body checks.

    Features:

        - One skill type for elevator certifications
        - Three certifications seeded
        - Certificate number and issuer on each CV line
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_certificate_hiss',
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
