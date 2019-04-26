# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
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
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from datetime import datetime
import werkzeug
import pytz


class website_punch_clock(http.Controller):

    @http.route(['/punchclock/<model("res.users"):user>', '/punchclock/<model("res.users"):user>/<string:clicked>', '/punchclock'], type='http', auth="user", csrf=False, website=True)
    def signin_user(self, user=False, clicked=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        if not user:
            return werkzeug.utils.redirect("/punchclock/%s" %request.env.uid,302)
        if clicked:
            user.employee_ids[0].attendance_action_change()
        if post.get('signin_button',False): 
            user.employee_ids[0].attendance_action_change()
            
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        last = user.employee_ids[0].last_attendance_id.check_in if user.employee_ids[0].attendance_state == 'checked_in' else user.employee_ids[0].last_attendance_id.check_out
        last = pytz.utc.localize(datetime.strptime(last, '%Y-%m-%d %H:%M:%S')).astimezone(tz).replace(tzinfo=None)
    
        ctx = {
            'user' : user,
            'signed_in': _("Punch Out") if user.employee_ids[0].attendance_state == 'checked_in' else _("Punch In"), 
            'last': last,
            'attendance': user.employee_ids[0].last_attendance_id,
            'employee': user.employee_ids[0],           
            }
    

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
