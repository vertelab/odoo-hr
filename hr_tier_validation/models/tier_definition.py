from odoo import models, fields, api, _


class TierDefinition(models.Model):
    _inherit = 'tier.definition'

    hr_department_id = fields.Many2one('hr.department', string="Department")