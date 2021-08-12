from odoo import models, fields, api, _


class TimesheetSchema(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.depends('employee_id')
    def _get_employee_work_hours(self):
        for rec in self:
            if rec.employee_id:
                rec.schema_time = rec.employee_id.resource_calendar_id.hours_per_day * 5
            else:
                rec.schema_time = 0

    schema_time = fields.Float(string="Schema Time", compute=_get_employee_work_hours)
