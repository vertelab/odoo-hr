# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2017 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
import werkzeug
import pytz


class website_punch_clock(http.Controller):

    @http.route(['/punchclock/<model("res.users"):user>', '/punchclock/<model("res.users"):user>/<string:clicked>', '/punchclock'], type='http', auth="user", website=True)
    def punchclock(self, user=False, clicked=False, **post):
        if not user:
            return request.redirect('/punchclock/%s' %request.env.uid, 302)
        employee = user.employee_ids[0]
        if clicked:
            employee.attendance_action_change()
        if post.get('signin_button',False):
            employee.attendance_action_change()

        last=employee.last_sign
        tz = pytz.timezone(user.partner_id.tz or 'UTC')

        last = pytz.utc.localize(datetime.strptime(last or "1969-01-01 01:01:01", '%Y-%m-%d %H:%M:%S')).astimezone(tz).replace(tzinfo=None)

        ctx = {
            'employee' : employee,
            'user' : user,
            'signed_in': _("Punch Out") if employee.state == 'present' else _("Punch In"),
            'last': _('Last') + _(' %s %s') %(_("punched in") if employee.state == 'present' else _("punched out"), fields.Datetime.to_string(last)[:16]),
        }
        if hasattr(employee, 'presence_check'):
            ctx['presence'] = _('Check out') if employee.presence_check() else _('Check in')
            
        return request.render('mobile_punch_clock.mobile_punch_clock_template', ctx)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    def get_base_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @api.one
    def send_mail(self):
        template = self.env.ref('mobile_punch_clock.mobile_punch_clock_email_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = {
            'default_model': 'hr.employee',
            'default_res_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
        }
        composer = self.env['mail.compose.message'].with_context(ctx).create({})
        composer.send_mail()
