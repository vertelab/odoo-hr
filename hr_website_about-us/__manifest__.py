# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<http://vertel.se>).
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
    'name': 'HR Website About Us',
    'version': '14.0.0.0',
    'category': 'Employee',
    'summary': 'Show employee on webpage.',
    'description': """To show or hide employee on public webpage.
Edit settings for non-public users.
Users and groups >> Groups.
Click "Accesses".
Add new line and enter Model (Employed) and "Read" access.

     """,
    'author': 'Vertel AB',
    'website': 'https://www.vertel.se',
    'depends': ['website', 'portal'],
    'data': [
        'views/about-us_view.xml',
    ],
    'application': True,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
