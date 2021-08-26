from odoo import models, fields, api, _


class TimesheetSchema(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.depends('timesheet_ids.non_billable', 'timesheet_ids.unit_amount')
    def _compute_timesheet_details(self):
        for sheet in self:
            if sheet.timesheet_ids:
                sheet.non_billable_time = sum(sheet.timesheet_ids.filtered(
                    lambda x: x.non_billable).mapped("unit_amount"))
                sheet.billable_time = sum(sheet.timesheet_ids.filtered(
                    lambda x: not x.non_billable).mapped("unit_amount"))
            else:
                sheet.non_billable_time = 0
                sheet.billable_time = 0

    non_billable_time = fields.Float(string="Non-Billable", compute=_compute_timesheet_details, store=True)

    billable_time = fields.Float(string="Billable", compute=_compute_timesheet_details, store=True)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    non_billable = fields.Boolean(string="Non-Billable", default=False)

    @api.depends('non_billable', 'unit_amount')
    def _compute_timesheet_details(self):
        for sheet in self:
            if sheet.non_billable:
                sheet.non_billable_time = sheet.unit_amount
                sheet.billable_time = 0
            else:
                sheet.billable_time = sheet.unit_amount
                sheet.non_billable_time = 0

    non_billable_time = fields.Float(string="Non-Billable", compute=_compute_timesheet_details, store=True)

    billable_time = fields.Float(string="Billable", compute=_compute_timesheet_details, store=True)

