from odoo import models, api, fields, _
from odoo.exceptions import UserError


class HROvertime(models.Model):
    _name = 'hr.overtime'

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    project_id = fields.Many2one('project.project', string="Project")
    time_report_id = fields.Many2one('hr_timesheet.sheet', string="Time Report")
    hours = fields.Float(string="Hours")
    type = fields.Selection([('Wanted', 'Wanted'), ('Ordered', 'Ordered')], string="Type", default='Wanted')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'To Approve'),
                              ('approved', 'Approved'), ('declined', 'Declined')],
                             string="State", default='draft')

    def action_submit_request(self):
        self.state = 'submitted'

    def action_approve_request(self):
        self.state = 'approved'

    def action_decline_request(self):
        self.state = 'declined'
