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
from datetime import datetime, timedelta


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
    type_id = fields.Many2one(comodel_name='hr.certification.type', string='Type', required=True,track_visibility='onchange')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',track_visibility='onchange')
    is_signed = fields.Boolean(string="Signed",help="This certification/agreement is signed by the employee",track_visibility='onchange')
    date_start = fields.Date(string="Start",default=lambda s: fields.Date.today(),track_visibility='onchange')
    @api.one
    @api.depends('date_start','type_id')
    @api.onchange('date_start','type_id')
    def _date_end(self):
        self.date_end = fields.Date.to_string(fields.Datetime.from_string(self.date_start) + timedelta(days=self.type_id.validity_days)) if self.type_id and self.type_id.validity_days else None
    date_end = fields.Date(string="End",default=lambda s: fields.Date.today(),help="Leave blank if there is no expiery",track_visibility='onchange')
    template = fields.Binary(string='Template',related='type_id.template')
    description = fields.Text()

    @api.model
    def _get_state_selection(self):
        states = self.env['hr.certification.state'].search([], order='sequence')
        return [(state.technical_name, state.name) for state in states]
    
    @api.model
    def _default_state_id(self):
        return self.env['hr.certification.state'].search([], order='sequence', limit=1)
    
    @api.one
    def _compute_state(self):
        if not self.state_id:
           self.state = self.env['hr.certification.state'].search([], order='sequence', limit=1).technical_name
        else:
            self.state = self.state_id.technical_name 

    @api.one
    def _set_state(self):
        self.state_id = self.env['hr.certification.state'].search([('technical_name','=',self.state)]).id

    state_id = fields.Many2one(comodel_name='hr.certification.state', string='State', default=_default_state_id, track_visibility='onchange')
    state = fields.Selection(selection=_get_state_selection, compute='_compute_state',inverse='_set_state',store=True)
    
    @api.one
    def do_sign(self):
        self.sudo().is_signed = True
        self.sudo().state = self.env.ref('hr_certifications.state_active').technical_name
        #~ raise Warning('Hello')

    @api.model
    def create(self, vals):
        res = super(hr_certification, self).create(vals)
        if res.employee_id:
            res.message_subscribe_users(user_ids=[res.employee_id.user_id.id])
        return res
    
  #~ def message_subscribe_users(self, cr, uid, ids, user_ids=None, subtype_ids=None, context=None):
        #~ """ Wrapper on message_subscribe, using users. If user_ids is not
            #~ provided, subscribe uid instead. """
        #~ if user_ids is None:
            #~ user_ids = [uid]
        #~ partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]
        #~ result = self.message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)
        #~ if partner_ids and result:
            #~ self.pool['ir.ui.menu'].clear_cache()
        #~ return result


class hr_certification_type(models.Model):
    """
    The agreement (NDA), license or certification (drivers, forklift), 
    diploma that the employee has signed
    """
    _name = 'hr.certification.type'
    _description = 'Employee Certification Type'

    name = fields.Char(string='Name')
    description = fields.Text()
    mode = fields.Selection([('cert','Certification'),('agreement','Agreement'),('permission','Permission'),],string='Mode')
    validity_days = fields.Integer(string="Validity",help="Number of days before it deprecates")
    template = fields.Binary(string="Template",help="Document to sign")

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
    is_signed = fields.Boolean(string="Signed",help="This asset is signed by the employee",track_visibility='onchange')
    

    @api.one
    def do_sign(self):
        self.sudo().is_signed = True

    @api.model
    def create(self, vals):
        res = super(account_asset_asset, self).create(vals)
        if res.employee_id:
            res.message_subscribe_users(user_ids=[res.employee_id.user_id.id])
        return res


class account_asset_category(models.Model):
    _inherit = 'account.asset.category'

    field_code = fields.Boolean('Code field')
    field_serialno = fields.Boolean('Serial Number field')
    field_imei = fields.Boolean('IMEI field',help="International Mobile Equipment Identity (Phone) ")
    field_license_plate = fields.Boolean('License Plate field',help="Licence plate on a vehicle")
    
class res_users(models.Model):
    _inherit = 'res.users'

    @api.one
    def _employee_id(self):
        self.employee_id = self.env['hr.employee'].search([('user_id','=',self.id)])