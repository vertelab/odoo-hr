# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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
    'name': 'Invoice on Timesheets',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
Generate your Invoices from Expenses, Timesheet Entries.
========================================================

Module to generate invoices based on costs (human resources, expenses, ...).

You can define price lists in analytic account, make some theoretical revenue
reports.""",
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'depends': ['hr_timesheet', 'report'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_timesheet_invoice_data.xml',
        'views/hr_timesheet_invoice_view.xml',
        'hr_timesheet_invoice_wizard.xml',
        #~ 'report/hr_timesheet_invoice_report.xml',
        #~ 'report/report_analytic_view.xml',
        #~ 'report/hr_timesheet_invoice_report_view.xml',
        'wizard/hr_timesheet_analytic_profit_view.xml',
        'wizard/hr_timesheet_invoice_create_view.xml',
        'wizard/hr_timesheet_invoice_create_final_view.xml',
        'views/report_analyticprofit.xml',
    ],
    'demo': ['demo/hr_timesheet_invoice_demo.xml'],
    'test': ['test/test_hr_timesheet_invoice.yml',
             'test/test_hr_timesheet_invoice_no_prod_tax.yml',
             'test/hr_timesheet_invoice_report.yml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
