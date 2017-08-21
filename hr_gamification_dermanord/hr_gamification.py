# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2017- Vertel AB (<http://vertel.se>).
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
from openerp import http
from openerp.http import request
import pytz
import logging
_logger = logging.getLogger(__name__)

class Workout(http.Controller):
    
    def convert_to_local(self, timestamp, tz_name):
        dt = fields.Datetime.from_string(timestamp)
        local_dt = pytz.utc.localize(dt).astimezone(pytz.timezone(tz_name))
        return fields.Datetime.to_string(local_dt)
    
    @http.route(['/hr/attendance/training'], type='json', auth="user", website=True)
    def training(self, employee_id=None, **kw):
        employee = request.env['hr.employee'].browse(int(employee_id))
        work = request.env['project.task.work'].search([('task_id', '=', request.env.ref('hr_gamification_dermanord.task_training').id)]).create({
            'name': 'training pass (%s) - %s' %(self.convert_to_local(fields.Datetime.now(), request.env.context.get('tz') or request.env.user.tz), employee.name),
            'hours': 0.0,
            'date': fields.Datetime.now(),
            'user_id': employee.user_id.id,
            'task_id': request.env.ref('hr_gamification_dermanord.task_training').id,
        })
        return 'done' if work else ''

    @http.route(['/hr/attendance/workout'], type='json', auth="user", website=True)
    def workout(self, employee_id=None, **kw):
        employee = request.env['hr.employee'].browse(int(employee_id))
        work = request.env['project.task.work'].search([('task_id', '=', request.env.ref('hr_gamification_dermanord.task_workout').id)]).create({
            'name': 'workout pass (%s) - %s' %(self.convert_to_local(fields.Datetime.now(), request.env.context.get('tz') or request.env.user.tz), employee.name),
            'hours': 0.0,
            'date': fields.Datetime.now(),
            'user_id': employee.user_id.id,
            'task_id': request.env.ref('hr_gamification_dermanord.task_workout').id,
        })
        return 'done' if work else ''
