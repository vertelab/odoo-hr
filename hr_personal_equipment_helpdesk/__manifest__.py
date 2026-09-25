# -*- coding: utf-8 -*-
{
    'name': 'HR: Personal Equipment Helpdesk',
    'version': '18.0.1.0.0',
    'summary': """Allow users submit helpdesk ticket for their Personal Equipment.""",
    'category': 'Helpdesk',
    'description': '''
Personal Equipment Helpdesk
===========================

    Allow users submit helpdesk ticket for their Personal Equipment.

    Features:

        - Web integration: Exposes HTTP endpoints for external systems.
        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on helpdesk.ticket.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_personal_equipment_helpdesk',
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
