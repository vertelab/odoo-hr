# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<http://vertel.se>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'HR Website About Us Calendar',
    'version': '14.0.0.0',
    'summary': 'Book meeting with employee.',
    'category': 'Human Resources',
    'description': """Glue module for HR Website About us. Implementing calendar button to book meeting with employees with sales role.""",
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/about-us',
    'repository': 'https://github.com/vertelab/odoo-hr',
    'depends': [        
        'website_calendar_ce',
        'hr_website_about-us',
        ],
    'data': [        
        'views/about-us_view.xml',
        'views/hr_view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
