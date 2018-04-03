# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP,  Open Source Management Solution,  third party addon
#    Copyright (C) 2004-2018 Vertel AB (<http://vertel.se>).
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

import logging
_logger = logging.getLogger(__name__)

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    certification_ids = fields.One2many(comodel_name="hr.certification",inverse_name='employee_id')
    @api.one
    def _cert_count(self):
        self.cert_count = len(self.certification_ids)
    cert_count = fields.Integer(compute='_cert_count')

    assets_ids = fields.One2many(comodel_name="account.asset.asset",inverse_name='employee_id')
    
    @api.one
    def _asset_count(self):
        self.asset_count = len(self.assets_ids)
    asset_count = fields.Integer(compute='_asset_count')

class hr_certification(models.Model):
    """
   An agreement, license or certification. It can also be a physical key, phone
    """
    _name = 'hr.certification'
    _description = "Employee Certification"
    _inherit = ['mail.thread']
    
    
    name = fields.Char(string="Name", translate=True, required=True)
    color = fields.Integer(string='Color Index')
    type_id = fields.Many2one(comodel_name='hr.certification.type', string='Type', required=True,)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',)
    product_id = fields.Many2one(comodel_name='product.product')
    serial_no = fields.Char()
    imei_no = fields.Char()
    #~ mode = fields.Selection(related='type_id.mode', string="Mode", help="")

    @api.model
    def _get_state_selection(self):
        states = self.env['hr.certification.state'].search([], order='sequence')
        return [(state.technical_name, state.name) for state in states]
    
    @api.model
    def _default_state_id(self):
        return self.env['hr.certification.state'].search([], order='sequence', limit=1)
    
    @api.one
    def _compute_state(self):
        self.state = self.state_id.technical_name

    state_id = fields.Many2one(comodel_name='hr.certification.state', string='State', required=True, default=_default_state_id, track_visibility='onchange')
    state = fields.Selection(selection=_get_state_selection, compute='_compute_state')
    


class hr_certification_type(models.Model):
    """
    The agreement (NDA), license or certification (drivers, forklift), 
    diploma that the employee has signed
    """
    _name = 'hr.certification.type'
    _description = 'Employee Certification Type'

    name = fields.Char(string='Name')
    description = fields.Text()
    mode = fields.Selection([('cert','Certification'),('agreement','Agreement'),('permission','Permission'),('key','Key'),('card','Entry device'),('phone','Phone')],string='Mode')


class hr_certification_state(models.Model):
    """
    draft, pending, signed, expired/canceled
    """
    _name = 'hr.certification.state'

    name = fields.Char(string='Name', required=True)
    technical_name = fields.Char(string='Technical Name', required=True)
    sequence = fields.Integer(string='Sequence')
    fold = fields.Boolean(string='Folded in Kanban View', help='This stage is folded in the kanban view when there are no records in that state to display.')



class account_asset_asset(models.Model):
    _name = 'account.asset.asset'
    _inherit = ['account.asset.asset','mail.thread']
    employee_id = fields.Many2one(comodel_name='hr.employee',string="Employee",track_visibility='onchange')

    #~ field_code = fields.Char(string='Code',required=lambda s: s.category_id.field_code,invisible=lambda s: not s.category_id.field_code )
    field_code = fields.Char(string='Code',required=False,invisible=False)
    field_cat_code = fields.Boolean(related="category_id.field_code",invisible=True)
    field_serialno = fields.Char(string='Serial Number')
    field_cat_serialno = fields.Boolean(related="category_id.field_serialno",invisible=True)
    field_imei = fields.Char(string='IMEI',help="International Mobile Equipment Identity (Phone) ")
    field_cat_imei = fields.Boolean(related="category_id.field_imei",invisible=True)
    field_license_plate = fields.Char(string='License Plate',help="Licence plate on a vehicle")
    field_cat_license_plate = fields.Boolean(related="category_id.field_license_plate",invisible=True)


class account_asset_category(models.Model):
    _inherit = 'account.asset.category'

    field_code = fields.Boolean('Code field')
    field_serialno = fields.Boolean('Serial Number field')
    field_imei = fields.Boolean('IMEI field',help="International Mobile Equipment Identity (Phone) ")
    field_license_plate = fields.Boolean('License Plate field',help="Licence plate on a vehicle")
