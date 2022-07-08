# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate

import logging
import json
# ~ _logger = logging.getLogger(__name__)

class HrEmployeeBase(models.AbstractModel):
   
    _inherit = 'hr.employee.base'

    booking_type_id = fields.Many2one('calendar.booking.type', string='Booking type' , xdomain="[('employee_ids.user_id.id','=',self.employee_id)]")

    def get_website_url_employee(self):
        
        for employee in self:
            web_url = ''
            if employee.booking_type_id.website_url:
                web_url = employee.booking_type_id.website_url
                return web_url + '?employee_id=%s' % employee.id

    booking_type_domain = fields.Char(
       compute="_compute_booking_type_domain",
       readonly=True,
       store=False,
   )

    def _compute_booking_type_domain(self):
        for employee in self:
            employee.booking_type_domain = json.dumps(
               [('employee_ids', 'in', employee.id)]
            )