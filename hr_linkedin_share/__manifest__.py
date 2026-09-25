# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) {year} {company} info@vertel.se
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#
# https://www.odoo.com/documentation/14.0/reference/module.html
#
{
    'name': 'HR: Linkdin Share',
    'version': '18.0.1.0.0',
    'summary': "Shares job positions on LinkedIn.",
    'category': '', # Technical Settings|Localization|Payroll Localization|Account Charts|User types|Invoicing|Sales|Human Resources|Operations|Marketing|Manufacturing|Website|Theme|Administration|Appraisals|Sign|Helpdesk|Administration|Extra Rights|Other Extra Rights|
    'description': '''
Linkdin Share
=============

    Shares job positions on LinkedIn.

    Features:

        - UI Integration: Extends 1 view(s) in the Odoo interface.
        - Extends Odoo: Builds on hr.resume.line.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_linkedin_share',
    'images': ['static/description/banner.png'], 
    'license': 'AGPL-3',
    'depends': ["hr_skills_survey"],
    'data': ["views/resume_line_view.xml"],
    'demo': [],
    'application': False,
    'installable': True,    
    'auto_install': False,
}
