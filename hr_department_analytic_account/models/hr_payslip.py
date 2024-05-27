from odoo import models, fields, api, _


class Payslip(models.Model):
    _inherit = "hr.payslip"

    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True)