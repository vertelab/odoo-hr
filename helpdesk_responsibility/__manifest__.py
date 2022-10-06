# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Responsibility',
    'summary': 'To share responsibilities between helpdesk team.',
    'author': 'Vertel AB',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    'version': '14.0.0.1.0',
    'license': 'AGPL-3',
    'website': 'https://vertel.se/apps/hr',
    'description': """
        To share responsibilities between helpdesk team.
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
