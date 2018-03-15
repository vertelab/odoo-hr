# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Timesheet Invoice Rate',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
Compute invoice hour rate
=========================
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['hr_timesheet_sheet','hr_attendance'],
    'data': [
        'hr_timesheet_sheet_view.xml',
       ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
