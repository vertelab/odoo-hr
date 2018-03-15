# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Timesheet Holidays Tab',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """View spent and earned holiday on the timesheets.
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['hr_timesheet_sheet','hr_holidays', 'hr_weekly_working_hours'],
    'data': [
        'hr_timesheet_sheet_view.xml',
       ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
