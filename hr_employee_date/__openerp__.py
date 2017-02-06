# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Employee Contract Start Date',
    'version': '1.1',
    'category': 'Human Resources',
    'licence': 'AGPL-3',
    'description': """
Employee start date
===================

Field on hr.employee that finds first employee date from
hr.contract
    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['hr_contract'],
    'data': [
        'hr_employee_date_view.xml',
       ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
