# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class HrPersonalEquipmentRequestWeb(models.TransientModel):

    _name = "hr.personal.equipment.request.web"
    _description = "This model allows to create a personal equipment request from website"

    name = fields.Char(compute="_compute_name")
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=False,
        default=lambda self: self._default_employee_id(),
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        required=False,
        domain=[("is_personal_equipment", "=", True)],
    )
    quantity = fields.Integer(default=1)

    observations = fields.Text()

    def _default_employee_id(self):
        return self.env.user.employee_ids[:1]

    @api.depends("employee_id")
    def _compute_name(self):
        for rec in self:
            rec.name = _("Personal Equipment Request by %s") % rec.employee_id.name

    @api.model
    def create(self, vals):
        req = self.env['hr.personal.equipment.request'].create({
            'employee_id': vals.get('employee_id'),
            'observations': vals.get('observations'),
        })

        if req:
            self.env['hr.personal.equipment'].create({
                'equipment_request_id': req.id,
                'product_id': vals.get('product_id'),
                'quantity': vals.get('quantity'),
            })

        return super().create(vals)
