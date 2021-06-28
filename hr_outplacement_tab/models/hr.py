from odoo import models, fields, api, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    outplacement_ids = fields.One2many(comodel_name='outplacement', inverse_name='employee_id',
                                       string='Assigned outplacements')
