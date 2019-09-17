# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import datetime
from openerp import models,api,fields, _
from openerp import http
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)

class hr_employee(models.Model):
    _inherit = "hr.employee"
    
    present = fields.Boolean(string='Present in office', default=False)

    @api.multi
    def attendance_action_change(self):
        if self.env.context is None:
            self.env.context = {}

        is_remote = self.env.context.get('remote', False)
        for employee in self:
            if is_remote:
                employee.present = False
            else:
                employee.present = True
        
        return super(hr_employee, self).attendance_action_change()

    @api.one
    def presence_change(self):
        if self.present:
            self.present = False
        else:
            self.present = True
        
    @api.multi
    def presence_check(self):
        return self.present

class attendancePresenceReport(http.Controller):

    # Used by hr_attendance_terminal
    @http.route(['/hr/attendance/presence_status'], type='json', auth="user", website=True)
    def presence_validate(self, employee_id=None, **kw):
        employee = request.env['hr.employee'].browse(int(employee_id))
        if employee.presence_check():
            return 'in'
        return 'out'
    
    # Used by hr_attendance_terminal
    @http.route(['/hr/attendance/presence'], type='json', auth="user", website=True)
    def present(self, employee_id=None, **kw):
        employee = request.env['hr.employee'].browse(int(employee_id))
        employee.presence_change()
        return 'done'

    # Used by hr_attendance_terminal
    @http.route(['/hr/attendance/employees_presence'], type='json', auth="user", website=True)
    def check_employees(self, **kw):
        employees = request.env['hr.employee'].search([('active', '=', True), ('id', '!=', request.env.ref('hr.employee').id)]).filtered(lambda e: e.present == True)
        employees_list = {}
        for e in employees:
            employees_list[e.name] = e.image_small
        if len(employees_list) > 0:
            return employees_list
        else:
            return ''

    # Used by mobile_punch_clock
    @http.route(['/punchclock/presence/<model("res.users"):user>', '/punchclock/presence/<model("res.users"):user>/<string:clicked>', '/punchclock/presence'], type='http', auth="user", website=True)
    def punchclock(self, user=False, clicked=False, **post):
        if not user:
            return request.redirect('/punchclock/%s' %request.env.uid, 302)
        if clicked:
            user.employee_ids[0].presence_change()
        if post.get('presence_button',False):
            user.employee_ids[0].presence_change()

        return request.redirect('/punchclock/%s' %request.env.uid, 302)

