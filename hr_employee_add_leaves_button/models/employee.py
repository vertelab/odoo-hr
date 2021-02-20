from odoo import models, fields, api, exceptions, _
from datetime import datetime

class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    present = fields.Boolean("Present", compute='compute_present')

    def compute_present(self):
        today = datetime.today().date()
        leave_obj = self.env['hr.leave']
        for emp in self:
            present = True
            leaves = leave_obj.search([('employee_id', '=', emp.id),
                                       ('state', '=', 'validate')])
            for leave in leaves:
                if leave.request_date_from and leave.request_date_to and leave.request_date_from >= today and leave.request_date_from <= today:
                    present = False
                    continue
            if present:
                emp.present = True
            else:
                emp.present = False
