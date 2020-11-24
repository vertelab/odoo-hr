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


from odoo import http
from odoo.addons.hr_employee_ciam_server.controllers.token import \
    validate_token, valid_response

_logger = logging.getLogger(__name__)


class CiamServer(http.Controller):
    pass

    @validate_token
    @http.route("/v1/user/get", methods=["POST"],
                type="http", auth="none", csrf=False)
    def user_get(self, *args, **kwargs):
        res = [
            {'firstName': 'test',
             'lastName': 'testsson',
             'personNr': None,
             'customerNr': None,
             'signature': None,
             'personIdentifier': None,
             'userId': 'c8de9565-4e45-4568-903a-a2eff4637bc9',
             'orgId': None,
             'eMail': 'test@example.com',
             'username': 'test@example.com',
             'status': None},
            {'firstName': 'Test',
             'lastName': 'testberg',
             'personNr': '195905041475',
             'customerNr': None,
             'signature': None,
             'personIdentifier': None,
             'userId': 'c91a5ebd-2c0a-4e21-9ba4-bd7b3dc0a20a',
             'orgId': None,
             'eMail': 'test@example2.com',
             'username': 'test@example2.com',
             'status': None},
            {'firstName': 'Test1',
             'lastName': 'Webportal',
             'personNr': None,
             'customerNr': None,
             'signature': None,
             'personIdentifier': None,
             'userId': '3091207e-4842-44f0-8f16-ef3bba9b62cf',
             'orgId': None,
             'eMail': 'test1.webportal@example.com',
             'username': 'test1.webportal@example.com',
             'status': None},
        ]
        # data = [self.client(r) for r in res]
        return valid_response(res)

    @validate_token
    @http.route("/v1/user/add", methods=["POST"],
                type="http", auth="none", csrf=False)
    def user_add(self, *args, **kwargs):
        message = 'OK. User added'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/user/update", methods=["POST"],
                type="http", auth="none", csrf=False)
    def user_update(self, *args, **kwargs):
        message = 'Successful update'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/user/delete", methods=["POST"],
                type="http", auth="none", csrf=False)
    def user_delete(self, *args, **kwargs):
        message = 'Successful delete'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/user/requestDelete", methods=["POST"],
                type="http", auth="none", csrf=False)
    def user_requestDelete(self, *args, **kwargs):
        message = 'Successful requestDelete'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/role/assign", methods=["POST"],
                type="http", auth="none", csrf=False)
    def role_assign(self, *args, **kwargs):
        message = 'Successful assign'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/role/listAssigned", methods=["POST"],
                type="http", auth="none", csrf=False)
    def role_listAssigned(self, *args, **kwargs):
        message = 'Successful listAssigned'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/role/listAvailable", methods=["POST"],
                type="http", auth="none", csrf=False)
    def role_listAvailable(self, *args, **kwargs):
        message = 'Successful listAvailable'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/role/revoke", methods=["POST"],
                type="http", auth="none", csrf=False)
    def role_revoke(self, *args, **kwargs):
        message = 'Successful revoke'
        return valid_response([{"message": message}])

    @validate_token
    @http.route("/v1/role/request", methods=["POST"],
                type="http", auth="none", csrf=False)
    def role_request(self, *args, **kwargs):
        message = 'Successful request'
        return valid_response([{"message": message}])
