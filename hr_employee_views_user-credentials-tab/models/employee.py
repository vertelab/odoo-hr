from odoo import models, fields, api, exceptions, _
from datetime import datetime

class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    groups_id = fields.Many2many('res.groups', 'rel_employee_group', 'emp_id', 'rel_emp_group',
                                compute='compute_emp_groups')

    def compute_emp_groups(self):
        for emp in self:
            if emp.user_id:
                for group in emp.user_id.groups_id:
                    emp.groups_id = [(4, group.id)]