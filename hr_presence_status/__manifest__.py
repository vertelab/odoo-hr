# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Presence Status Control',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
        Control Employees Presence from User Profile
    """,
    'depends': ['base', 'hr_holidays', 'hr', 'web'],
    'data': [
        'views/assets.xml',

    ],
    'demo': [],
    'qweb': [
        'static/src/xml/partner_im_status.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
