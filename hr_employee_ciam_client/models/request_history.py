# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
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
################################################################################

import logging

from odoo import api, http, models, tools, SUPERUSER_ID, fields

_logger = logging.getLogger(__name__)


class RequestHistory(models.Model):
    _name = 'request.history'
    _description = "Request History"
    _rec_name = 'url'

    config_id = fields.Many2one('ciam.client.config',
                                string="Config ID")
    url = fields.Char(string='Url')
    method = fields.Char(string='Method')
    payload = fields.Char(string='Payload')
    request_headers = fields.Char(string='Request Headers')
    response_headers = fields.Char(string='Response Headers')
    params = fields.Char(string='Params')
    response_code = fields.Char(string='Response Code')
    message = fields.Char(string='Message')
