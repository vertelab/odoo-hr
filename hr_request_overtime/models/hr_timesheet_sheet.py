from odoo import models, fields, api, _


class HRTimesheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.depends('employee_id', 'name')
    def _compute_overtime(self):
        for _rec in self:
            if _rec.employee_id and _rec.name:
                overtime_ids = self.env['hr.overtime'].search([
                    ('employee_id', '=', _rec.employee_id.id),
                    ('time_report_id', '=', _rec.id),
                    ('state', '=', 'approved')
                ])
                _rec.approved_overtime = sum([overtime_id.hours for overtime_id in overtime_ids])
            else:
                _rec.approved_overtime = 0

    approved_overtime = fields.Float(string="Approved Overtime", compute=_compute_overtime, copy=False)
