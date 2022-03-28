# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<https://vertel.se>).
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
    'name': 'HR Overtime',
    'summary': 'HR Overtime',
    'author': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'description': """
        HR Overtime'
    """,
    'depends': ['hr', 'hr_timesheet_sheet', 'hr_timesheet_schema', 'hr_timesheet_nonbillable'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_overtime_view.xml',
        'views/hr_timesheet_sheet_view.xml',
    ],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
