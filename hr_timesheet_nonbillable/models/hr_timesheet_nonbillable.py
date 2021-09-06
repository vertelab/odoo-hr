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


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('timesheet_ids', 'company_id.timesheet_encode_uom_id')
    def _compute_timesheet_total_duration(self):
        for sale_order in self:
            timesheets = sale_order.timesheet_ids if self.user_has_groups(
                'hr_timesheet.group_hr_timesheet_approver') else sale_order.timesheet_ids.filtered(
                lambda t: t.user_id.id == self.env.uid)
            total_time = 0.0
            for timesheet in timesheets.filtered(lambda t: not t.non_allow_billable and not t.non_billable):
                # Timesheets may be stored in a different unit of measure, so first we convert all of them to the reference unit
                total_time += timesheet.unit_amount * timesheet.product_uom_id.factor_inv
            # Now convert to the proper unit of measure
            total_time *= sale_order.timesheet_encode_uom_id.factor
            sale_order.timesheet_total_duration = total_time

    def action_view_timesheet(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale_timesheet.timesheet_action_from_sales_order")
        action['context'] = {
            'search_default_billable_timesheet': True
        }  # erase default filters
        if self.timesheet_count > 0:
            action['domain'] = [('so_line', 'in', self.order_line.ids), ('non_billable', '=', False)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_compute_delivered_quantity_domain(self):
        """ Hook for validated timesheet in addionnal module """
        return [('project_id', '!=', False), ('non_allow_billable', '=', False), ('non_billable', '=', False)]

    def _recompute_qty_to_invoice(self, start_date, end_date):
        """ Recompute the qty_to_invoice field for product containing timesheets

            Search the existed timesheets between the given period in parameter.
            Retrieve the unit_amount of this timesheet and then recompute
            the qty_to_invoice for each current product.

            :param start_date: the start date of the period
            :param end_date: the end date of the period
        """
        lines_by_timesheet = self.filtered(lambda sol: sol.product_id and sol.product_id._is_delivered_timesheet())
        domain = lines_by_timesheet._timesheet_compute_delivered_quantity_domain()
        domain = expression.AND([domain, [
            '|',
            ('timesheet_invoice_id', '=', False),
            ('timesheet_invoice_id.state', '=', 'cancel')]])
        if start_date:
            domain = expression.AND([domain, [('date', '>=', start_date)]])
        if end_date:
            domain = expression.AND([domain, [('date', '<=', end_date)]])
        domain = expression.AND([domain, [('non_billable', '=', True)]])
        mapping = lines_by_timesheet.sudo()._get_delivered_quantity_by_analytic(domain)

        for line in lines_by_timesheet:
            line.qty_to_invoice = mapping.get(line.id, 0.0)


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
