from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(
        selection_add=[("hr_department", "Department address")],
        ondelete={"hr_department": "cascade"},
    )
