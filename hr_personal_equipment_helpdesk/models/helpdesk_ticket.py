from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    hr_personal_equipment_id = fields.Many2one("hr.personal.equipment", string="Personal Equipment", readonly=True)



