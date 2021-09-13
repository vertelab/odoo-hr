from  odoo import models, fields, api, _


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    address_ids = fields.One2many('hr.department.address', 'department_id', string="Address")


class HRAddress(models.Model):
    _name = 'hr.department.address'

    name = fields.Char(string="Address")
    department_id = fields.Many2one('hr.department', string="Department")
