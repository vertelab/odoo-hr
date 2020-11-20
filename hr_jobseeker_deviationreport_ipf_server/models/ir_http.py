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

import werkzeug
import werkzeug.exceptions
import werkzeug.routing
import werkzeug.urls
import werkzeug.utils

import json
import datetime
import logging

from odoo.http import request
from odoo import api, http, models, tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _handle_exception(cls, exception):

        response_header = request.httprequest.headers
        if response_header.get('AF-TrackingId'):
            message = ''
            code = None
            if isinstance(exception, werkzeug.exceptions.InternalServerError):
                code = 500
                message = exception
            elif isinstance(exception, werkzeug.exceptions.HTTPException) \
                    and exception.code in (400, 404,):
                code = exception.code
                if exception.code == 400:
                    message = 'Bad Request'
                elif exception.code == 404:
                    message = 'Not Found'

            if code:
                headers = {
                    "AF-TrackingId": response_header.get('AF-TrackingId'),
                    "AF-SystemId": response_header.get('AF-SystemId'),
                    "AF-EndUserId": response_header.get('AF-EndUserId'),
                    "AF-Environment": response_header.get('AF-Environment'),
                    "x-amf-mediaType": "application/json"}
                return werkzeug.wrappers.Response(
                    status=code,
                    headers=headers,
                    content_type="application/json; charset=utf-8",
                    response=json.dumps({"message": message},
                                        default=datetime.datetime.isoformat,
                                        ),
                )
        else:
            return super(IrHttp, cls)._handle_exception(exception)
