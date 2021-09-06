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
    'name': 'HR Timesheet NonBillable',
    'version': '14.0.0.0',
    'category': 'Employee',
    'summary': 'To be able to report non-billable time when reporting time.',
    'description': """
        To be able to report non-billable time when reporting time.
    
        - be able to indicate non-billable time on an activity (e.g. in the details tab of the time report)
        - compile billable and non billable time on the time report
        - In report do follow-up Compare schedule time, invoiced time and non-invoiced time
    """,
    'author': 'Vertel AB',
    'website': 'https://www.vertel.se',
    'depends': ['hr_timesheet_sheet', 'sale_timesheet'],
    'data': [
        'views/account_analytic_line_views.xml',
        'views/hr_timesheet_nonbillable_view.xml',
    ],
    'application': True,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
