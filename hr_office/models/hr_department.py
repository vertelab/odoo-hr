from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = "hr.department"

    office_code = fields.Char(string="Office code") #fyrställig
    organisation_number = fields.Char(string="Organisaiton Number") #sektionsnummer
    operation_ids = fields.Many2many(comodel_name='hr.operation', string="Operations")
    partner_id = fields.Many2one(comodel_name="res.partner")
    


class HrOperation(models.Model):
    _name = "hr.operation"

    name = fields.Char(string="Name")
    opening_hours = fields.Char(string = 'Opening hours')
    personal_service_opening = fields.Char(string="Opening hours for personal service")
    x500_id = fields.Char(string="x500 id")
    
    department_id = fields.Many2one(comodel_name='hr.department', string="Office")
    accessibilites_ids = fields.One2many(comodel_name='hr.location.accessibility', inverse_name='location_id')

    partner_id = fields.Many2one('res.partner', string="Partner") 
    visitation_address_id = fields.Many2one('res.partner', string="Visitation address")
    mailing_address_id = fields.Many2one('res.partner', string="Mailing address")

    location_id = fields.Many2one(comodel_name='hr.location', string="Location")

class HrLocation(models.Model):

    name = fields.Char(string="Name")
    location_code = fields.Char(string="Location code")
    workplace_number = fields.Char(string="Workplace number")

    operation_ids = fields.One2many(comodel_name='hr.operation', string="Operations", inverse_name='location_id')

    user_ids = fields.One2many(comodel_name='res.users', string="Users", inverse_name='location_id')

    @api.model
    def get_workplace_number(self, location_code):
        location = self.search([('location_code', '=', location_code)])
        if location:
            return location.workplace_number
        else:
            return False


class HrlocationAccessibility(models.Model):
    _name = "hr.location.accessibility"

    location_id = fields.Many2one(comodel_name="hr.location")
    name = fields.Char(string="Type")
    description = fields.Char(string="Description")