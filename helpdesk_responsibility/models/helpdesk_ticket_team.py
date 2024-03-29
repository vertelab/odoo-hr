from odoo import models, fields, api, _
from datetime import date, datetime, timedelta, time
from calendar import monthrange
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"
    
    helpdesk_user_ids = fields.Many2many('res.users', 'helpdesk_ticket_user_rel', string='Helpdesk Users')
    ticket_rotation = fields.Boolean(string='Ticket Rotation')
    number_of_events = fields.Integer(compute='_ticketteam_event_count')
    periodicity = fields.Selection([('daily','Daily'),('weekly','Weekly'),('monthly','Monthly')])


    def rotate_ticket(self,cronjob=None):
        """
        Rotate team members
        """

        if cronjob:
                team_ids = self.env['helpdesk.ticket.team'].search([('ticket_rotation', '=', True)])
                for team_id in team_ids:
                    if team_id and team_id.helpdesk_user_ids:
                        _logger.error(f"{team_id.periodicity=}")
                        _logger.error(f"{cronjob=}")
                        if team_id.periodicity == cronjob:

                            userlist = team_id.helpdesk_user_ids
                            users = len(userlist)
                            low_seq = team_id.helpdesk_user_ids[0].sequence
                            hi_seq = team_id.helpdesk_user_ids[0].sequence
                            user_id = None

                            if users > 1:
                                for user in userlist:   # Loop through and rotate users
                                    userseq = user.sequence
                                    if userseq <= low_seq:
                                        low_seq = userseq
                                        low_seq_user = user
                                    elif userseq >= hi_seq:
                                        hi_seq = userseq
                                    user.sequence = userseq - 1
                                low_seq_user.sequence = hi_seq

                                for user in userlist:   # Loop through again after rotation and get the user with the lowest sequence nr
                                    userseq = user.sequence
                                    if userseq <= low_seq:
                                        low_seq = userseq
                                        low_seq_user = user
                                    elif userseq >= hi_seq:
                                        hi_seq = userseq

                                user_id = low_seq_user

                            elif users == 1:
                                user_id = userlist[0]

                            if user_id:                    
                                self._create_ticket_event(team_id, user_id)


    def _create_ticket_event(self, team_id, user_id):
        """
        Create a calendar event for each helpdesk team
        """
        eventname = None
        if team_id.periodicity == 'daily':
            responsible = _('Responsible:')
            eventname = f'{team_id.name} {responsible} {user_id.name}'
            start_date = date.today()
            stop_date = date.today()

        elif team_id.periodicity == 'weekly':
            week = date.today().isocalendar()[1]
            responsible = _('Responsible for week')
            eventname = f'{team_id.name} {responsible} {week}: {user_id.name}'
            today = date.today()
            diff = today.isoweekday() - 1
            start_date = today - timedelta(days=diff)
            stop_date = start_date + timedelta(days=4)  # stops at friday(work week). Set this to 6 to get whole week.

        elif team_id.periodicity == 'monthly':
            month = (_('January'),_('February'),'Mars','April',_('May'),_('June'),
            _('July'),_('August'),'September',_('October'),'November','December')
            m_index = int(datetime.now().strftime('%m')) -1
            responsible = _('Responsible for')
            eventname = f'{team_id.name} {responsible} {month[m_index]}: {user_id.name}'
            this_year = datetime.now().year
            this_month = datetime.now().month
            start_date = datetime(this_year,this_month,1)
            if this_month + 1 > 12:
                this_year += 1
                this_month = 1
            else:
                this_month += 1
            stop_date = datetime(this_year,this_month,1) - timedelta(days=1)

        user_id = team_id.helpdesk_user_ids.filtered(lambda x: x.id == user_id.id)
        if eventname:
            partner_id = user_id.partner_id.id
            partner_ids = [(6,0,[partner_id])]
            self.env['calendar.event'].create({
                'name': eventname,
                'start_date': start_date,
                'stop_date': stop_date,
                'user_id': user_id.id,
                'partner_id': partner_id,
                'partner_ids': partner_ids,
                'helpdesk_event': True,
                'allday': True,
                'helpdesk_ticket_team': team_id.id
            })

    def _ticketteam_event_count(self,team_id=False):
        if team_id:
            own_id = team_id.id
        else:
            own_id = self.id
        ticketteam_events = self.env['calendar.event'].search([('helpdesk_ticket_team','=',own_id)])
        self.number_of_events = len(ticketteam_events)
        
    def list_events(self):
        ctx = dict(self.env.context)
        ctx.update({'from_helpdesk':  True, 'helpdesk_ticket_team': self.id})
        return {
            'name':'Team ticket events','res_model':'calendar.event','view_model':'list',
            'view_mode': 'tree,form','target':'main','type':'ir.actions.act_window',
            'context': ctx,'domain': [('helpdesk_ticket_team','=',self.id)]
            }


class Users(models.Model):
    _inherit = 'res.users'

    sequence = fields.Integer(string='Sequence', default=1)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'


    def _compute_helpdesk_event(self):
        if 'from_helpdesk' in self.env.context:
            self.helpdesk_event = True
        else:
            self.helpdesk_event = False

    def _compute_helpdesk_ticket_team(self):
        if 'helpdesk_ticket_team' in self.env.context:
            return self.env.context['helpdesk_ticket_team']
        else:
            return False

    helpdesk_event = fields.Boolean(string='Helpdesk Event', default=False, compute='_compute_helpdesk_event')
    helpdesk_ticket_team = fields.Many2one('helpdesk.ticket.team', default=_compute_helpdesk_ticket_team)
