from matplotlib.pyplot import cla
from odoo import models, fields, api
from datetime import date, datetime, timedelta


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    
    helpdesk_user_ids = fields.Many2many('res.users', 'helpdesk_ticket_user_rel', string='Helpdesk Users')

    ticket_rotation = fields.Boolean(string='Ticket Rotation')

    def rotate_ticket(self):
        """
        Check calender event for who has been assigned to a week in the previous week 
        """
        team_id = self.env['helpdesk.ticket.team'].search([('ticket_rotation', '=', True)], limit=1)
        if team_id and team_id.helpdesk_user_ids:
            user_id = team_id.helpdesk_user_ids[0]
            event_id = self._check_last_event()
            if event_id:
                user_id = team_id.helpdesk_user_ids.filtered(lambda x: x.id == event_id.user_id.id)
                next_user_id = team_id.helpdesk_user_ids.filtered(lambda x: x.sequence == user_id.sequence + 1)
                if not next_user_id:
                    next_user_id = team_id.helpdesk_user_ids.filtered(lambda x: x.sequence == 1)
                self._create_ticket_event(team_id, next_user_id)
            
            if not event_id:
                self._create_ticket_event(team_id, user_id)
    
    def _check_last_event(self):
        """
        Check if there is a calendar event for last week
        """
        last_week = date.today() - timedelta(days=7)
        
        event_id = self.env['calendar.event'].search([
            ('start_date', '>=', last_week),
            ('stop_date', '<=', last_week + timedelta(days=4)),
            ('helpdesk_event', '=', True)
        ], limit=1)
        if event_id:
            return event_id
        else:
            return False

    def _create_ticket_event(self, team_id, user_id):
        """
        Create a calendar event for each helpdesk team
        """
        team_id = self.env['helpdesk.ticket.team'].search([('ticket_rotation', '=', True)], limit=1)
        user_id = team_id.helpdesk_user_ids.filtered(lambda x: x.id == user_id.id)
        self.env['calendar.event'].create({
            'name': 'Helpdesk Support for Week %s ' % (date.today().isocalendar()[1]),
            'start_date': date.today(),
            'stop_date': date.today() + timedelta(days=4),
            'user_id': user_id.id,
            'helpdesk_event': True,
            'allday': True,
        })


class Users(models.Model):
    _inherit = 'res.users'

    sequence = fields.Integer(string='Sequence', default=1)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    helpdesk_event = fields.Boolean(string='Helpdesk Event', default=False)
