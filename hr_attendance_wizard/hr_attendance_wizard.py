# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2016- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class hr_attendance_add_wizard(models.TransientModel):
    _name = 'hr.attendance.add.wizard'
    
    employee_id = fields.Many2one('hr.employee', 'Employee', required = True)
    date_from = fields.Datetime('Sign In Time', required = True)
    date_to = fields.Datetime('Sign Out Time', required = True)
    
    @api.multi
    def create_attendances(self):
        if self.date_from >= self.date_to:
            raise Warning(_("Can't create attendance records! Sign out must come after sign in."))
        if self.env['hr.attendance'].search([('name', '>=', self.date_from), ('name', '<=', self.date_to), ('action', 'in', ['sign_in', 'sign_out']), ('employee_id', '=', self.employee_id.id)]):
            raise Warning(_("Can't create attendance records! There are already attendances registered in the specified period."))
        prev_so = self.env['hr.attendance'].search([('name', '<', self.date_from), ('action', 'in', ['sign_in', 'sign_out']), ('employee_id', '=', self.employee_id.id)], order = 'name DESC', limit = 1)
        next_so = self.env['hr.attendance'].search([('name', '>', self.date_to), ('action', 'in', ['sign_in', 'sign_out']), ('employee_id', '=', self.employee_id.id)], order = 'name ASC', limit = 1)
        if (prev_so and prev_so.action == 'sign_in') or (next_so and next_so.action == 'sign_out'):
            raise Warning(_("Can't create attendance records! Sign in must be followed by sign out.%s%s") %(
                prev_so and prev_so.action == 'sign_in' and (_(" Previous attendance (%s (GMT))  is a Sign In.") % prev_so.name) or '',
                next_so and next_so.action == 'sign_out' and (_(" Next attendance (%s (GMT))  is a Sign Out.") % next_so.name) or ''))
        self.env.cr.execute("INSERT INTO hr_attendance (name, action, employee_id) VALUES (%s, %s, %s)", (self.date_from, 'sign_in', self.employee_id.id))
        self.env.cr.execute("INSERT INTO hr_attendance (name, action, employee_id) VALUES (%s, %s, %s)", (self.date_to, 'sign_out', self.employee_id.id))
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
