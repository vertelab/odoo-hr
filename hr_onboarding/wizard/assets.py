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


class hr_employee_assets_wizard(models.TransientModel):
    _name = 'hr.employee.assets.wizard'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee')
    mobile_pad_ids = fields.One2many(string='Mobile/Pad', comodel_name='hr.employee.assets.line.wizard', inverse_name='mobile_pad_employee_assets_wizard_id')
    computer_ids = fields.One2many(string='Computer', comodel_name='hr.employee.assets.line.wizard', inverse_name='computer_employee_assets_wizard_id')
    entry_ids = fields.One2many(string='Entry', comodel_name='hr.employee.assets.line.wizard', inverse_name='entry_employee_assets_wizard_id')
    has_mobile_pad = fields.Boolean(string='Has Mobile/Pad', related='employee_id.job_id.has_mobile_pad')
    has_computer = fields.Boolean(string='Has Computer', related='employee_id.job_id.has_computer')
    has_key = fields.Boolean(string='Has Key', related='employee_id.job_id.has_key')

    @api.multi
    def confirm(self):
        for a in self.mobile_pad_ids:
            a.mobile_pad_id.employee_id = self.employee_id.id
            a.mobile_pad_id.is_signed = a.mobile_pad_is_signed
        for c in self.computer_ids:
            c.computer_id.employee_id = self.employee_id.id
            c.computer_id.is_signed = c.computer_is_signed
        for e in self.entry_ids:
            e.entry_id.employee_id = self.employee_id.id
            e.entry_id.is_signed = e.entry_is_signed


class hr_employee_assets_line_wizard(models.TransientModel):
    _name = 'hr.employee.assets.line.wizard'

    mobile_pad_employee_assets_wizard_id = fields.Many2one(comodel_name='hr.employee.assets.wizard')
    mobile_pad_category = fields.Many2one(string='Mobile/Pad Category', comodel_name='account.asset.category', domain="[('journal_id.type', '=', 'purchase'), ('account_asset_id.user_type.code', '=', 'asset')]")
    mobile_pad_id = fields.Many2one(string='Mobile/pad', comodel_name='account.asset.asset', domain="[('employee_id', '=', False), ('category_id', '=', mobile_pad_category), ('state', '=', 'draft')]")
    mobile_pad_is_signed = fields.Boolean(string='Signed')
    computer_employee_assets_wizard_id = fields.Many2one(comodel_name='hr.employee.assets.wizard')
    computer_category = fields.Many2one(string='Computer Category', comodel_name='account.asset.category', domain="[('journal_id.type', '=', 'purchase'), ('account_asset_id.user_type.code', '=', 'asset')]")
    computer_id = fields.Many2one(string='Computer', comodel_name='account.asset.asset', domain="[('employee_id', '=', False), ('category_id', '=', computer_category), ('state', '=', 'draft')]")
    computer_is_signed = fields.Boolean(string='Signed')
    entry_employee_assets_wizard_id = fields.Many2one(comodel_name='hr.employee.assets.wizard')
    entry_category = fields.Many2one(string='Entry Category', comodel_name='account.asset.category', domain="[('journal_id.type', '=', 'purchase'), ('account_asset_id.user_type.code', '=', 'asset')]")
    entry_id = fields.Many2one(string='Entry', comodel_name='account.asset.asset', domain="[('employee_id', '=', False), ('category_id', '=', entry_category), ('state', '=', 'draft')]")
    entry_is_signed = fields.Boolean(string='Signed')
