# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP,  Open Source Management Solution,  third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation,  either version 3 of the
#    License,  or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not,  see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.survey.controllers.main import WebsiteSurvey
from openerp.exceptions import except_orm, Warning
import logging
_logger = logging.getLogger(__name__)


class WebsiteSurvey(WebsiteSurvey):

    @http.route(['/survey/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        res = super(WebsiteSurvey, self).submit(survey, **post)
        user_input = request.env['survey.user_input'].search([('token', '=', post['token'])])
        if user_input.employee_id:
            user_input.save_values('employee_id')
        return res

    @http.route(['/survey/check/<string:token>'], type='http', methods=['GET'], auth='public', website=True)
    def check(self, token, **post):
        user_input = request.env['survey.user_input'].search([('token', '=', token)])
        if user_input.employee_id:
            user_input.save_values('employee_id')
        return 'Hello World'
