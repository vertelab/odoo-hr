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
from odoo.tools.config import config
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
import logging
import time

# Osäker på om denna behövs verkligen
class hr_attendance(http.Controller):
    @http.route('/hr_hw_server/command', auth='public', type='json')
    def hr_request(self, password=None, command=None, **params):
    	pwd = request.env['ir.config.param'].sudo().get_param('hr_hw_server.password')
    	if not pwd or (pwd != password):
    		# TODO: Skicka 401
    		raise Warning('Wrong password!')
    	if command == 'check_barcode':
    		check = request.env['hr.employee'].sudo().search([('barcode', '=', params.get('barcode'))])
    		if check:
    			return True
    		else:
    			return False
        
        elif command == 'check_in_out':
        	return request.env['hr.employee'].sudo().attendance_scan(params.get('barcode'))        	
