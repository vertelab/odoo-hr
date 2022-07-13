# -*- coding: utf-8 -*-

from odoo import registry, SUPERUSER_ID, http
from odoo.api import Environment
from odoo.addons.bus.controllers import main
from odoo.fields import Datetime
from odoo.http import Controller, request, route


class UserStatus(http.Controller):

    @route('/get/status', type="json", auth="user")
    def get_partner_status(self, model='res.partner', partner_id=None):
        partner_id = request.env[model].with_user(request.env.uid).search([('id', '=', partner_id)])
        return partner_id.im_status
    
    @route('/set/status', type="json", auth="user")
    def set_partner_status(self, model='res.partner', partner_id=None):
        partner_id = request.env[model].with_user(request.env.uid).search([('id', '=', partner_id)])
        partner_id.im_status = 'away'
        print(partner_id.im_status)
        return self.get_partner_status(model, partner_id.id)