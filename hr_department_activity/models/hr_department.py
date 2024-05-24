from odoo import models, fields, api, _


class HRDepartment(models.Model):
    _name = 'hr.department'
    _inherit = ['hr.department', 'mail.activity.mixin']