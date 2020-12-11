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


class ClientConfig(models.Model):
    _name = 'ciam.client.config'
    _rec_name = 'url'

    url = fields.Char(string='Url',
                      required=True)
    client_secret = fields.Char(string='Client Secret',
                                required=True)
    client_id = fields.Char(string='Client ID',
                            required=True)
    environment = fields.Selection(selection=[('U1', 'U1'),
                                              ('I1', 'I1'),
                                              ('T1', 'IT'),
                                              ('T2', 'T2'),
                                              ('PROD', 'PROD'), ],
                                   string='Environment',
                                   default='u1',
                                   required=True)
    request_history_ids = fields.One2many('request.history',
                                          'config_id',
                                          string='Requests')

    def request_call(self, method, url, payload=False,
                     headers=False, params=False):

        response = requests.request(method=method,
                                    url=url,
                                    data=json.dumps(payload),
                                    headers=headers,
                                    params=params,
                                    verify=False)

        self.create_request_history(method="POST",
                                    url=url,
                                    response=response,
                                    payload=json.dumps(payload),
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
        self.env['request.history'].create(values)

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

    def user_get(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {'username': 'test'}
        url = self.get_url('v1/user/get')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)

        print(response.text)

    def user_add(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {'personNr': 1955010127777,
                   'firstName': 'Pelle',
                   'lastName': 'Svensson',
                   'eMail': 'pelle.svensson@bolaget.se',
                   'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06',
                   'username': 'pelle.svensson.14',
                   'password': '123',
                   'customerNr': '444', 'status': "1"}

        url = self.get_url('v1/user/add')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def user_update(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {'personNr': 1955010127777,
                   'userId': 'Pelle',
                   'personIdentifier': 'Svensson',
                   'customerNr': 'pelle.svensson@bolaget.se', }
        url = self.get_url('v1/user/update')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def user_delete(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {'personNr': 1955010127777,
                   'userId': 3243,
                   'personIdentifier': '1232ffrr',
                   'customerNr': 54545, }
        url = self.get_url('v1/user/delete')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def user_requestDelete(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {'userId': 3243}

        url = self.get_url('v1/user/requestDelete')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def role_assign(self):

        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {
            'roleName': 'role_name',
            'userId': '3243',
            'custId': '32442',
            'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'
        }

        url = self.get_url('v1/role/assign')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def role_listAssigned(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {
            'userId': '3243',
        }

        url = self.get_url('v1/role/listAssigned')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def role_listAvailable(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {'userId': '3243',
                   'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'}

        url = self.get_url('v1/role/listAvailable')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def role_revoke(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {
            'roleName': 'role_name',
            'userId': '3243',
            'custId': '32442',
            'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'
        }

        url = self.get_url('v1/role/revoke')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def role_request(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {
            'roleName': 'role_name',
            'userId': '3243',
            'custId': '32442',
            'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'
        }
        url = self.get_url('v1/role/request')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)
