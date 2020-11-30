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

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, http, models, tools, SUPERUSER_ID, fields

_logger = logging.getLogger(__name__)


class ApfApiError(Exception):
    pass


class ClientConfig(models.Model):
    _name = 'ipf.report.client.config'
    _rec_name = 'url'

    url = fields.Char(string='Url',
                      required=True)
    client_secret = fields.Char(string='Client Secret',
                                required=True)
    client_id = fields.Char(string='Client ID',
                            required=True)
    environment = fields.Selection(selection=[('u1', 'U1'),
                                              ('i1', 'I1'),
                                              ('t1', 'IT'),
                                              ('t2', 'T2'),
                                              ('prod', 'PROD'), ],
                                   string='Environment',
                                   default='u1',
                                   required=True)
    request_history_ids = fields.One2many('ipf.report.request.history',
                                          'config_id',
                                          string='Requests')

    def request_call(self, method, url, payload=None,
                     headers=None, params=None):

        response = requests.request(method=method,
                                    url=url,
                                    data=payload,
                                    headers=headers,
                                    params=params)
        self.create_request_history(method=method,
                                    url=url,
                                    response=response,
                                    payload=payload,
                                    headers=headers,
                                    params=params)

        return response

    def create_request_history(self, method, url, response, payload=False,
                               headers=False, params=False):
        values = {'config_id': self.id,
                  'method': method,
                  'url': url,
                  'payload': payload,
                  'request_headers': headers,
                  'response_headers': response.headers,
                  'params': params,
                  'response_code': response.status_code}
        values.update(message=json.loads(response.content))
        self.env['ipf.report.request.history'].create(values)

    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {
            'x-amf-mediaType': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': "AF-SystemId",
            'AF-EndUserId': "AF-EndUserId",
            'AF-Environment': self.environment,
        }
        return headers

    def get_url(self, path):
        if self.url[-1] == '/':
            url = self.url + path
        else:
            url = self.url + '/' + path
        return url

    @api.model
    def post_report(self, payload):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}

        url = self.get_url('v1/genomforande-avvikelserapport-created')
        response = self.request_call(
            method="POST",
            url=url,
            payload=json.dumps(payload),
            headers=self.get_headers(),
            params=querystring)
        if response.status_code != 200:
            raise ApfApiError(response.text)
        return response

    def testing_post_report(self):
        payload = {
            "genomforande_referens": "123456789",
            "id": "4aaaad4f-b2e0-4a99-b9a0-06bab83bf069",
            "datum_for_rapportering": "2020-11-04",
            "arbetssokande": {
                "personnummer": "191212121212",
                "fornamn": "Test",
                "efternamn": "Testsson"
            },
            "ansvarig_arbetsformedlare": {
                "funktionsbrevlada": "test@test.se"
            },
            "leverantor": {
                "leverantorsnamn": "test",
                "rapportor": {
                    "fornamn": "fornamn",
                    "efternamn": "efternamn"
                },
                "kanummer": "10009858"
            },
            "franvaro": {
                "orsak": "Sjuk",
                "datum": "2020-11-04",
                "heldag": True,
                "starttid": "08:00",
                "sluttid": "17:00"
            }
        }
        response = self.post_report(payload)
