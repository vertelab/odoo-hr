from odoo import models, api, fields, _


class Partner(models.Model):
    _inherit = 'res.partner'

    department_id = fields.Many2many('hr.department', string="Department")
