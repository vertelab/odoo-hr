# Copyright 2025 Vertel AB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time
import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError,UserError


class ResourceCalendarPublicHoliday(models.Model):
    _inherit = "resource.calendar.leaves"

    def fetch_public_holidays(self):
        # ~ raise Exception(self.env.context)
        
        calendar = self.env['resource.calendar'].browse(self.env.context.get('default_calendar_id',False))
        public_holidays = self.env['calendar.public.holiday'].search([]) # TODO What if we have several public holidays for the same year different countries?
        for ph in public_holidays:
            if ph.line_ids:
                if len(calendar.global_leave_ids.filtered(lambda d: d.date_from.date() == ph.line_ids[0].date)) == 0:
                    for day in ph.line_ids:
                        self.env['resource.calendar.leaves'].create({
                            'name':       day.name,
                            'date_from':  datetime.combine(day.date, time(0, 0)),
                            'date_to':    datetime.combine(day.date, time(23, 59)),
                            'calendar_id':calendar.id,
                            })
        
        # ~ return {
            # ~ 'type': 'ir.actions.act_window',
            # ~ 'name': 'Public Holiday',
            # ~ 'res_model': 'calendar.public.holiday',
            # ~ 'view_mode': 'form',
            # ~ 'view_id': self.env.ref('calendar_public_holiday.view_calendar_public_holiday_form').id,
            # ~ 'res_id': cal.id,  
            # ~ 'target': 'current',
        # ~ }
