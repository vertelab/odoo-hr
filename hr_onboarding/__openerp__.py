# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Employee Onboarding',
    'version': '1.1',
    'category': 'Human Resources',
    'licence': 'AGPL-3',
    'description': """
Employee Onboarding
===================

Define stages for onboard personel

This module depends on OpenHRMS

    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': [
        'hr_employee_updation',
        'survey_save',
        'hr_recruitment',
        'hr_certifications',
        'account_asset',
        'report_scribus',
    ],
    'data': [
        'data/survey_data.xml',
        'report/employee_business_card_report.xml',
        'wizard/company_info_view.xml',
        'wizard/contract_info_view.xml',
        'wizard/assets_view.xml',
        'wizard/certification_view.xml',
        'data/stage_data.xml',
        'views/hr_view.xml',
        'views/onbording_stage_view.xml',
        'security/ir.model.access.csv',
        # ~ 'security/rules.xml',
       ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
