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
    'name': 'HR: Skills Certificate',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Certificate number and issuer on CV certification lines.',
    'category': 'Human Resources',
    'description': '''
HR: Skills Certificate
=======================

    Odoo stores certifications as CV lines (hr.resume.line with
    display_type = certification) and, with hr_skills_survey, tracks their
    expiry through expiration_status. What it does not store is the
    certificate itself: the number printed on it and who issued it.

    That is fine for a course taken in Odoo — the survey result is the
    proof. It is not fine for an external certification. "Anna has a forklift
    licence" is a claim; "Anna has forklift licence TLP10-2024-04471, issued
    by X" is something a supervisory authority can verify.

    This module adds the three fields that make an external certification
    verifiable:

        certificate_number    the number on the certificate
        certificate_issuer    who issued it
        certificate_url       where it can be checked

    It is deliberately thin. It does not model certification types, expiry
    rules or renewal — Odoo already has hr.skill.type, date_end and
    expiration_status. Adding a second status machine would mean two
    sources of truth for "is this still valid?".

    Industry bridges
    ----------------
    Which certifications an industry needs is customer knowledge, not
    generic. Those live in separate modules that depend on this one:

        hr_certificate_arbetsmiljo   Heta arbeten, Fallskydd, OSA
        hr_certificate_esa           Elsäkerhet
        hr_certificate_hiss          Hissinstallation
        hr_certificate_restaurant    Livsmedelshygien, alkoholservering

    A metal shop installs arbetsmiljo + esa. An elevator company installs
    all four. An office installs none.

    Features:

        - Certificate number, issuer and verification URL on CV lines
        - Visible only when the line is a certification
        - Search by certificate number
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_skills_certificate',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    'depends': [
        'hr_skills',
    ],
    'data': [
        'views/hr_resume_line_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
