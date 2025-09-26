# -*- coding: utf-8 -*-
{
    'name': 'HR: Personal Equipment Helpdesk',
    'version': '1.0',
    'summary': """Allow users submit helpdesk ticket for their Personal Equipment""",
    'category': 'Helpdesk',
    'description': """
        Allow users submit helpdesk ticket for their Personal Equipment
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'depends': ["helpdesk_mgmt", "hr_personal_equipment_request"],
    'data': [
        "views/helpdesk_ticket_templates.xml",
        "views/helpdesk_ticket_view.xml",
        "security/ir.model.access.csv",
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
