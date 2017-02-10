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
    _inherit = 'hr.attendance.add.wizard'
    
    @api.multi
    def get_values_dict(self, type):
        res = super(hr_attendance_add_wizard, self).get_values_dict(type)
        res['sheet_id'] = self.env['hr.attendance']._get_current_sheet(self.employee_id.id, self.date_from if type == 'sign_in' else self.date_to)
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
