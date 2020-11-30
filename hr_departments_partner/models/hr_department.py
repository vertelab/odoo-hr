from odoo import models, api, fields, _


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    address_id = fields.Many2many('res.partner', string="Address")
