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
import datetime
import pytz
import logging
_logger = logging.getLogger(__name__)

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    max_training_count_per_day = fields.Integer(string='Max training per day', help='This parameter presents how many time this employee can do training each day. Set to 0 if this employee is not allowed to go training. Leave empty to unlimit.', default=1)
    max_training_count_per_week = fields.Integer(string='Max training per week', help='This parameter presents how many time this employee can do training each week. Set to 0 if this employee is not allowed to go training. Leave empty to unlimit.', default=2)
    max_workout_count_per_day = fields.Integer(string='Max workout per day', help='This parameter presents how many time this employee can do training each day.  Set to 0 if this employee is not allowed to go workout. Leave empty to unlimit.', default=1)

class Workout(http.Controller):

    def convert_to_local(self, timestamp, tz_name):
        dt = fields.Datetime.from_string(timestamp)
        local_dt = pytz.utc.localize(dt).astimezone(pytz.timezone(tz_name))
        return fields.Datetime.to_string(local_dt)

    @http.route(['/hr/attendance/training_validate'], type='json', auth="user", website=True)
    def training_validate(self, employee_id=None, **kw):
        today = datetime.date.today()
        dates_in_week = [today + datetime.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
        employee = request.env['hr.employee'].browse(int(employee_id))
        contract = employee.contract_ids[0]
        if contract:
            works_in_day = request.env['project.task.work'].search([('task_id', '=', request.env.ref('hr_gamification_dermanord.task_training').id)]).filtered(lambda w: w.date[:10] == fields.Datetime.now()[:10])
            if not contract.max_training_count_per_day and contract.max_training_count_per_day != 0:
                return 'confirm'
            elif len(works_in_day) < contract.max_training_count_per_day:
                works_in_week = request.env['project.task.work'].search([('task_id', '=', request.env.ref('hr_gamification_dermanord.task_training').id)]).filtered(lambda w: fields.Date.from_string(w.date[:10]) in dates_in_week)
                return 'confirm' if len(works_in_week) < contract.max_training_count_per_week else 'receipt'
            else:
                return 'receipt'
        else:
            return 'receipt'

    @http.route(['/hr/attendance/workout_validate'], type='json', auth="user", website=True)
    def workout_validate(self, employee_id=None, **kw):
        today = datetime.date.today()
        employee = request.env['hr.employee'].browse(int(employee_id))
        contract = employee.contract_ids[0]
        if contract:
            works_in_day = request.env['project.task.work'].search([('task_id', '=', request.env.ref('hr_gamification_dermanord.task_workout').id)]).filtered(lambda w: w.date[:10] == fields.Datetime.now()[:10])
            if not contract.max_workout_count_per_day and contract.max_workout_count_per_day != 0:
                return 'confirm'
            else:
                return 'confirm' if len(works_in_day) < contract.max_workout_count_per_day else 'receipt'
        else:
            return 'receipt'

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
