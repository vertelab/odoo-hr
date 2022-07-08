# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2021  https://vertel.se
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import models, fields, api, exceptions, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate

import logging
import json
# ~ _logger = logging.getLogger(__name__)



class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'website.seo.metadata', 'website.published.multi.mixin']
    
    public_info = fields.Char(string='Public Info')

    def _compute_website_url(self):
        super(HrEmployee, self)._compute_website_url()
        for employee in self:
            employee.website_url = '/aboutus'

    def sort_familyname(self,rec):
        return rec.sorted(lambda r: r.name.split(' ')[1])



# class HrEmployeeBase(models.AbstractModel):
#     _inherit = 'hr.employee.base'


#     public_info = fields.Char(string='Public Info')
#     booking_type_id = fields.Many2one('calendar.booking.type', string='Booking type' , xdomain="[('employee_ids.user_id.id','=',self.employee_id)]")

#     def get_website_url_employee(self):        
#         for employee in self:
#             web_url = ''
#             if employee.booking_type_id.website_url:
#                 web_url = employee.booking_type_id.website_url
#                 # return employee.booking_type_id.website_url + '?employee_id=%s' % employee.id
#                 return web_url + '?employee_id=%s' % employee.id

#     booking_type_domain = fields.Char(
#        compute="_compute_booking_type_domain",
#        readonly=True,
#        store=False,
#    )

#     def _compute_booking_type_domain(self):
#         for employee in self:
#             employee.booking_type_domain = json.dumps(
#                [('employee_ids', 'in', employee.id)]
            # )
