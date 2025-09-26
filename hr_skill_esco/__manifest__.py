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
# https://www.odoo.com/documentation/18.0/reference/module.html
#
{
    'name': 'HR: Skill ESCO',
    'version': '1.0',
    'summary': 'Extend HR with ESCO skills and skill type.',
    'category': 'Human Resources', # Technical Settings|Localization|Payroll Localization|Account Charts|User types|Invoicing|Sales|Human Resources|Operations|Marketing|Manufacturing|Website|Theme|Administration|Appraisals|Sign|Helpdesk|Administration|Extra Rights|Other Extra Rights|
    'description': """
         Den här modulen lägger till ESCO skill types och skills i HR.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/',
    'images': ['static/description/banner.png'], 
    'license': 'AGPL-3',
    'depends': ['hr_skills'],
    'data': [
        'views/hr_skills_esco_views.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,    
    'auto_install': False,
}
