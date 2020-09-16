from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = "hr.department"

    office_code = fields.Char(string="Office code") #fyrställig
    organisation_number = fields.Char(string="Organisaiton Number") #sektionsnummer
    location_ids = fields.Many2many(comodel_name='hr.campus', string="Campuses", inverse_name="office_id")
    


class Hrlocation(models.Model):
    _name = "hr.location"

    name = fields.Char(string="Name")
    opening_hours = fields.Char(string = 'Opening hours')
    personal_service_opening = fields.Char(string="Opening hours for personal service")
    workplace_number = fields.Char(string="Workplace number")
    location_code = fields.Char(string="Location code")
    
    department_ids = fields.Many2many(comodel_name='hr.department', string="Office")
    
    partner_id = fields.Many2one('res.partner', string="Partner") 
    visitation_address_id = fields.Many2one('res.partner', string="Visitation address")
    mailing_address_id = fields.Many2one('res.partner', string="Mailing address")

    accessibilites_ids = fields.One2many(comodel_name='hr.location.accessibility', inverse_name='location_id')

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