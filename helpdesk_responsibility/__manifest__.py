# -*- coding: utf-8 -*-
{
    'name': 'HR: Helpdesk Responsibility',
    'summary': 'To share responsibilities between helpdesk teams.',
    'author': 'Vertel AB',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    'version': '14.0.0.2.0',
    'license': 'AGPL-3',
    'website': 'https://vertel.se/apps/odoo-hr/helpdesk_responsibility',
    'description': """
        To share responsibilities between helpdesk teams.
    """,
    'depends': ['helpdesk_mgmt', 'calendar'],
    'data': [
        'views/helpdesk_ticket_team_view.xml',
        'views/calendar_event_view.xml',
        'data/ir_cron.xml',
    ],
    'application': False,
    'installable': True,
}
