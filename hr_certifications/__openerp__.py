# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Employee Certifications',
    'version': '1.1',
    'category': 'Human Resources',
    'licence': 'AGPL-3',
    'description': """
Employee Certifications
=======================

A possibility to store information of signed certifications, licenses, 
non-disclosure agreements and such documents. Loans of assets.

    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['hr','account_asset'],
    'data': [
        'hr_certifications_view.xml',
        'hr_certifications_data.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
       ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
