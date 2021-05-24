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
import json
from odoo import http
from odoo.addons.hr_jobseeker_deviationreport_ipf_server.controllers.token import \
    validate_token, valid_response, invalid_response
_logger = logging.getLogger(__name__)


class IpfReportServer(http.Controller):

    @validate_token
    @http.route("/v1/genomforande-avvikelserapport-created", methods=["POST"],
                type="http", auth="none", csrf=False)
    def leverantorsavrop(self, *args, **kwargs):

        values = http.request.httprequest.get_data()
        values_dict = json.loads(values.decode())
        missing_values = []

        return valid_response([])
