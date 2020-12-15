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
                                   default='T2',
                                   required=True)
    request_history_ids = fields.One2many('request.history',
                                          'config_id',
                                          string='Requests')

    def request_call(self, method, url, payload=False,
                     headers=False, params=False):
        
        response = requests.request(method=method,
                                    url=url,
                                    data=payload,
                                    headers=headers,
                                    params=params,
                                    verify=False)

        self.create_request_history(method="POST",
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
        self.env['request.history'].create(values)

    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {
            'Content-Type': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': "CRM",
            'AF-EndUserId': "*sys*",
            'AF-Environment': self.environment,
        }
        return headers

    def get_url(self, path):
        if self.url[-1] == '/':
            url = self.url + path
        else:
            url = self.url + '/' + path
        return url

    def test_user_get(self):
        data = {'username': 'test'}
        self.user_get(data)

    def user_get(self, data):
        querystring = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            }

        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        url = self.get_url('user/get')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)

        _logger.info(response.text)
        return response

    def test_user_add(self):
        data = { #note that some value need to be unique so change them everytime you want to run a test
            "personNr": "1955010127777",
            "firstName": "Test",
            "lastName": "Testson",
            "eMail": "test@test12.se", #unique
            "username": "test.testson.123", #unique
            "password": "abc12321", 
            "customerNr": "87654321", #unique, length of 8, not required
            "status": "1"
            }
        return self.user_add(data)

    def user_add(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        url = self.get_url('user/add')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_user_update(self):
        data = {'personNr': 1955010127777,
                   'userId': 'Pelle',
                   'personIdentifier': 'Svensson',
                   'customerNr': 'pelle.svensson@bolaget.se', }
        return self.user_update(data)

    def user_update(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        

        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        url = self.get_url('user/update')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_user_delete(self):
        data = {'personNr': 1955010127777,
                   'userId': 3243,
                   'personIdentifier': '1232ffrr',
                   'customerNr': 54545, }
        return self.user_delete(data)

    def user_delete(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        url = self.get_url('user/delete')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_user_requestDelete(self):
        data = {'userId': 3243}
        return self.user_requestDelete(data)

    def user_requestDelete(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }
        url = self.get_url('user/requestDelete')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_role_assign(self):
        data = {
            'roleName': 'role_name',
            'userId': '3243',
            'custId': '32442',
            'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'
        }
        return self.role_assign(data)

    def role_assign(self, data):

        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
       
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        url = self.get_url('role/assign')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_role_listAssigned(self):
        data = {
            'userId': '3243',
        }
        return self.role_listAssigned(data)

    def role_listAssigned(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        url = self.get_url('role/listAssigned')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_role_listAvailable(self):
        data = {'userId': '3243',
                   'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'}
        return self.role_listAvailable(data)

    def role_listAvailable(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }

        url = self.get_url('role/listAvailable')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_role_revoke(self):
        data = {
            'roleName': 'role_name',
            'userId': '3243',
            'custId': '32442',
            'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'
        }
        return self.role_revoke(data)

    def role_revoke(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }
        url = self.get_url('role/revoke')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_role_request(self):
        data = {
            'roleName': 'role_name',
            'userId': '3243',
            'custId': '32442',
            'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06'
        }
        return self.role_request(data)

    def role_request(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }
        url = self.get_url('role/request')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response

    def test_organization_get(self):
        data = {
            "customerNr": "711"
        }
        return self.organization_get(data)

    def organization_get(self, data):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        client = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }

        payload = {
            "client": client,
            "data": data
            }
        url = self.get_url('organization/get')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        _logger.info(response.text)
        return response
