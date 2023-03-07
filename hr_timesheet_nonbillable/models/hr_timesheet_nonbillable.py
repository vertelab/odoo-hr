from odoo import models, fields, api, _
from odoo.osv import expression


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

    @api.depends('project_id.allow_billable')
    def _compute_non_billable(self):
        for rec in self:
            if rec.project_id.allow_billable:
                rec.non_billable = rec.project_id.allow_billable
            else:
                rec.non_billable = False

    def _inverse_non_billable(self):
        pass

    non_billable = fields.Boolean(string="Non-Billable", default=False, compute=_compute_non_billable, store=True,
                                  inverse=_inverse_non_billable, compute_sudo=True)

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


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends('timesheet_ids')
    def _compute_timesheet_count(self):
        timesheet_data = self.env['account.analytic.line'].read_group([
            ('timesheet_invoice_id', 'in', self.ids), ('non_billable', '=', False)],
                                                                      ['timesheet_invoice_id'],
                                                                      ['timesheet_invoice_id'])
        mapped_data = dict([(t['timesheet_invoice_id'][0], t['timesheet_invoice_id_count']) for t in timesheet_data])
        for invoice in self:
            invoice.timesheet_count = mapped_data.get(invoice.id, 0)

    def _link_timesheets_to_invoice(self, start_date=None, end_date=None):
        """ Search timesheets from given period and link this timesheets to the invoice

            When we create an invoice from a sale order, we need to
            link the timesheets in this sale order to the invoice.
            Then, we can know which timesheets are invoiced in the sale order.
            :param start_date: the start date of the period
            :param end_date: the end date of the period
        """
        for line in self.filtered(lambda i: i.move_type == 'out_invoice' and i.state == 'draft').invoice_line_ids:
            sale_line_delivery = line.sale_line_ids.filtered(lambda sol: sol.product_id.invoice_policy == 'delivery'
                                                                         and sol.product_id.service_type == 'timesheet')
            if sale_line_delivery:
                domain = line._timesheet_domain_get_invoiced_lines(sale_line_delivery)
                if start_date:
                    domain = expression.AND([domain, [('date', '>=', start_date)]])
                if end_date:
                    domain = expression.AND([domain, [('date', '<=', end_date)]])
                domain = expression.AND([domain, [('non_billable', '=', False)]])
                timesheets = self.env['account.analytic.line'].sudo().search(domain)
                timesheets.write({'timesheet_invoice_id': line.move_id.id})

    def action_view_timesheet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Timesheets'),
            'domain': [('project_id', '!=', False), ('non_billable', '=', False)],
            'res_model': 'account.analytic.line',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _("""
                <p class="o_view_nocontent_smiling_face">
                    Record timesheets
                </p><p>
                    You can register and track your workings hours by project every
                    day. Every time spent on a project will become a cost and can be re-invoiced to
                    customers if required.
                </p>
            """),
            'limit': 80,
            'context': {
                'default_project_id': self.id,
                'search_default_project_id': [self.id]
            }
        }
