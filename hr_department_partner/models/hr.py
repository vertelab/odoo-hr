from  odoo import models, fields, api, _


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    address_ids = fields.One2many('hr.department.address', 'department_id', string="Address")
    department_number = fields.Char(string="Dept Number")


class HRAddress(models.Model):
    _name = 'hr.department.address'

    name = fields.Many2one('res.partner', string="Address", domain="[('type', '=', 'hr_department')]")
    department_id = fields.Many2one('hr.department', string="Department")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    department_number = fields.Char(string="Dept Number", related='department_id.department_number', store=True)


class HREmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    department_number = fields.Char(string="Dept Number")
