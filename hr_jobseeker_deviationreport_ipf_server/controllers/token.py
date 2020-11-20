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
import json
import logging
import werkzeug.wrappers
import datetime
import time
from odoo.http import request
import functools

_logger = logging.getLogger(__name__)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, bytes):
        return str(o)


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        try:
            client_secret = request.httprequest.args['client_secret']
            if not client_secret:
                raise
        except:
            return invalid_response("missing_client_secret",
                                    "client_secret is missing",
                                    401)
        try:
            client_id = request.httprequest.args['client_id']
            if not client_id:
                raise
        except:
            return invalid_response("ACCESS ERROR",
                                    "Missing access token in request header.",
                                    401)
        return func(self, *args, **kwargs)

    return wrap


def get_headers():
    response_header = request.httprequest.headers
    headers = {"AF-TrackingId": response_header.get('AF-TrackingId'),
               "AF-SystemId": response_header.get('AF-SystemId'),
               "AF-ResponseTime": int(round(time.time() * 1000)),
               "AF-Confidentiality": '1',
               "AF-Correctness": '2',
               "AF-Availability": '3',
               "AF-Traceability": '4',
               "x-amf-mediaType": "application/json"}
    return headers


def valid_response(data='', status=200, **kwargs):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {"count": len(data) if not isinstance(data, str) else 1,
            "data": data}
    data.update(kwargs)

    response = werkzeug.wrappers.Response(
        status=status,
        headers=get_headers(),
        content_type="application/json; charset=utf-8",
        response=json.dumps(data, default=default))
    return response


def invalid_response(typ, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    payload = {
        "error_id": "77506961-60e4-42be-aff6-123ca6d4eea3",
        "message": typ,
        "cause": {
            "system": "EIS",
            "code": "1002",
            "message": message and str(
                message) or "Wrong arguments (missing validation)",
            "error": [
                {
                    "falt": None,
                    "felkod": 1002,
                    "operation": None,
                    "kravnummer": None,
                    "meddelande": message and str(
                        message) or "Wrong arguments (missing validation)",
                    "valideringsregelTyp": None,
                    "valideringsregelvarde": None,
                    "entitetTyp": None,
                    "entitetId": None
                }
            ]
        }
    }

    response = werkzeug.wrappers.Response(
        status=status,
        headers=get_headers(),
        content_type="application/json; charset=utf-8",
        response=json.dumps(payload,
                            default=datetime.datetime.isoformat))
    return response
