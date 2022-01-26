from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(
        selection_add=[("hr_department", "Department address")],
        ondelete={"hr_department": "cascade"},
    )

    @api.depends('name')
    def _compute_partner_department(self):
        for _rec in self:
            if _rec.name:
                user_id = self.env['hr.department.address'].search([('name', '=', _rec.id)], limit=1)
                _rec.department_id = user_id.department_id.id
            else:
                _rec.department_id = False

    department_id = fields.Many2one('hr.department', string="Department", compute=_compute_partner_department)
