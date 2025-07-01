# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectTaskCreateSalesOrder(models.TransientModel):
    _inherit = 'project.task.create.sale.order'

    @api.depends('sale_line_id', 'price_unit', 'link_selection')
    def _compute_info_invoice(self):
        for line in self:
            domain = self.env['sale.order.line']._timesheet_compute_delivered_quantity_domain()
            timesheet = self.env['account.analytic.line'].read_group(domain + [
                ('task_id', '=', self.task_id.id), ('so_line', '=', False), ('non_billable', '=', False),
                ('timesheet_invoice_id', '=', False)], ['unit_amount'], ['task_id'])
            unit_amount = round(timesheet[0].get('unit_amount', 0), 2) if timesheet else 0
            if not unit_amount:
                line.info_invoice = False
                continue
            company_uom = self.env.company.timesheet_encode_uom_id
            label = _("hours")
            if company_uom == self.env.ref('uom.product_uom_day'):
                label = _("days")
            if line.link_selection == 'create' and line.price_unit:
                line.info_invoice = _("%(amount)s %(label)s will be added to the new Sales Order.",
                                      amount=unit_amount, label=label)
            else:
                line.info_invoice = _("%(amount)s %(label)s will be added to the selected Sales Order.",
                                      amount=unit_amount, label=label)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price
        else:
            self.price_unit = 0.0

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.sale_order_id = False
        self.sale_line_id = False

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        self.sale_line_id = False

    def action_link_sale_order(self):
        # link task to SOL
        self.task_id.write({
            'sale_line_id': self.sale_line_id.id,
            'partner_id': self.partner_id.id,
            'email_from': self.partner_id.email,
        })

        # assign SOL to timesheets
        self.env['account.analytic.line'].search([
            ('task_id', '=', self.task_id.id), ('so_line', '=', False),
            ('timesheet_invoice_id', '=', False),
            ('non_billable', '=', False)
        ]).write({
            'so_line': self.sale_line_id.id
        })

    def action_create_sale_order(self):
        sale_order = self._prepare_sale_order()
        sale_order.action_confirm()
        view_form_id = self.env.ref('sale.view_order_form').id
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action.update({
            'views': [(view_form_id, 'form')],
            'view_mode': 'form',
            'name': sale_order.name,
            'res_id': sale_order.id,
        })
        return action

    def _prepare_sale_order(self):
        # if task linked to SO line, then we consider it as billable.
        if self.task_id.sale_line_id:
            raise UserError(_("The task is already linked to a sales order item."))

        # create SO
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'company_id': self.task_id.company_id.id,
            'analytic_account_id': self.task_id.project_id.analytic_account_id.id,
        })
        sale_order.onchange_partner_id()
        sale_order.onchange_partner_shipping_id()
        # rewrite the user as the onchange_partner_id erases it
        sale_order.write({'user_id': self.task_id.user_id.id})
        sale_order.onchange_user_id()

        sale_order_line = self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'project_id': self.task_id.project_id.id,  # prevent to re-create a project on confirmation
            'task_id': self.task_id.id,
            'product_uom_qty': round(sum(
                self.task_id.timesheet_ids.filtered(
                    lambda t: not t.non_allow_billable and not t.so_line and not t.non_billable
                ).mapped('unit_amount')), 2),
        })

        # link task to SOL
        self.task_id.write({
            'sale_line_id': sale_order_line.id,
            'partner_id': sale_order.partner_id.id,
            'email_from': sale_order.partner_id.email,
        })

        # assign SOL to timesheets
        self.env['account.analytic.line'].search([
            ('task_id', '=', self.task_id.id),
            ('so_line', '=', False),
            ('timesheet_invoice_id', '=', False),
            ('non_billable', '=', False)
        ]).write({
            'so_line': sale_order_line.id
        })

        return sale_order
