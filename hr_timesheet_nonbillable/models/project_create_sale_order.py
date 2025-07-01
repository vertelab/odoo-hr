# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectCreateSalesOrder(models.TransientModel):
    _inherit = 'project.create.sale.order'

    @api.depends('analytic_account_id.line_ids')
    def _compute_timesheet_ids(self):
        for order in self:
            if order.analytic_account_id:
                order.timesheet_ids = self.env['account.analytic.line'].search(
                    [('so_line', 'in', order.order_line.ids),
                     ('amount', '<=', 0.0), ('non_billable', '=', False),
                     ('project_id', '!=', False)])
            else:
                order.timesheet_ids = []
            order.timesheet_count = len(order.timesheet_ids)

    @api.depends('sale_order_id', 'link_selection')
    def _compute_info_invoice(self):
        for line in self:
            tasks = line.project_id.tasks.filtered(lambda t: not t.non_allow_billable)
            domain = self.env['sale.order.line']._timesheet_compute_delivered_quantity_domain()
            timesheet = self.env['account.analytic.line'].read_group(domain + [('task_id', 'in', tasks.ids),
                                                                               ('so_line', '=', False),
                                                                               ('timesheet_invoice_id', '=', False),
                                                                               ('non_billable', '=', False)
                                                                               ],
                                                                     ['unit_amount'], ['task_id'])
            unit_amount = round(sum(t.get('unit_amount', 0) for t in timesheet), 2) if timesheet else 0
            if not unit_amount:
                line.info_invoice = False
                continue
            company_uom = self.env.company.timesheet_encode_uom_id
            label = _("hours")
            if company_uom == self.env.ref('uom.product_uom_day'):
                label = _("days")
            if line.link_selection == 'create':
                line.info_invoice = _("%(amount)s %(label)s will be added to the new Sales Order.",
                                      amount=unit_amount, label=label)
            else:
                line.info_invoice = _("%(amount)s %(label)s will be added to the selected Sales Order.",
                                      amount=unit_amount, label=label)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.sale_order_id = False

    def action_link_sale_order(self):
        task_no_sale_line = self.project_id.tasks.filtered(lambda task: not task.sale_line_id)
        # link the project to the SO line
        self.project_id.write({
            'sale_line_id': self.sale_order_id.order_line[0].id,
            'sale_order_id': self.sale_order_id.id,
            'partner_id': self.partner_id.id,
        })

        if self.pricing_type == 'employee_rate':
            lines_already_present = dict([(l.employee_id.id, l) for l in self.project_id.sale_line_employee_ids])
            EmployeeMap = self.env['project.sale.line.employee.map'].sudo()

            for wizard_line in self.line_ids:
                if wizard_line.employee_id.id not in lines_already_present:
                    EmployeeMap.create({
                        'project_id': self.project_id.id,
                        'sale_line_id': wizard_line.sale_line_id.id,
                        'employee_id': wizard_line.employee_id.id,
                    })
                else:
                    lines_already_present[wizard_line.employee_id.id].write({
                        'sale_line_id': wizard_line.sale_line_id.id
                    })

            self.project_id.tasks.filtered(lambda task: task.non_allow_billable).sale_line_id = False
            tasks = self.project_id.tasks.filtered(lambda t: not t.non_allow_billable)
            # assign SOL to timesheets
            for map_entry in self.project_id.sale_line_employee_ids:
                self.env['account.analytic.line'].search([
                    ('task_id', 'in', tasks.ids),
                    ('non_billable', '=', False),
                    ('employee_id', '=', map_entry.employee_id.id),
                    ('so_line', '=', False)]).write({'so_line': map_entry.sale_line_id.id})
        else:
            dict_product_sol = dict([(l.product_id.id, l.id) for l in self.sale_order_id.order_line])
            # remove SOL for task without product
            # and if a task has a product that match a product from a SOL, we put this SOL on task.
            for task in task_no_sale_line:
                if not task.timesheet_product_id:
                    task.sale_line_id = False
                elif task.timesheet_product_id.id in dict_product_sol:
                    task.write({'sale_line_id': dict_product_sol[task.timesheet_product_id.id]})

    def action_create_sale_order(self):
        # if project linked to SO line or at least on tasks with SO line, then we consider project as billable.
        if self.project_id.sale_line_id:
            raise UserError(_("The project is already linked to a sales order item."))
        # at least one line
        if not self.line_ids:
            raise UserError(_("At least one line should be filled."))

        if self.pricing_type == 'employee_rate':
            # all employee having timesheet should be in the wizard map
            timesheet_employees = self.env['account.analytic.line'].search([
                ('task_id', 'in', self.project_id.tasks.ids),
                ('non_billable', '=', False),
            ]).mapped('employee_id')
            map_employees = self.line_ids.mapped('employee_id')
            missing_meployees = timesheet_employees - map_employees
            if missing_meployees:
                raise UserError(_('The Sales Order cannot be created because you did not enter some employees that entered timesheets on this project. Please list all the relevant employees before creating the Sales Order.\nMissing employee(s): %s') % (', '.join(missing_meployees.mapped('name'))))

        # check here if timesheet already linked to SO line
        timesheet_with_so_line = self.env['account.analytic.line'].search_count([
            ('task_id', 'in', self.project_id.tasks.ids),
            ('non_billable', '=', False),
            ('so_line', '!=', False)
        ])
        if timesheet_with_so_line:
            raise UserError(_('The sales order cannot be created because some timesheets of this project are already '
                              'linked to another sales order.'))

        # create SO according to the chosen billable type
        sale_order = self._create_sale_order()

        view_form_id = self.env.ref('sale.view_order_form').id
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action.update({
            'views': [(view_form_id, 'form')],
            'view_mode': 'form',
            'name': sale_order.name,
            'res_id': sale_order.id,
        })
        return action

    def _create_sale_order(self):
        """ Private implementation of generating the sales order """
        sale_order = self.env['sale.order'].create({
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'analytic_account_id': self.project_id.analytic_account_id.id,
            'client_order_ref': self.project_id.name,
            'company_id': self.project_id.company_id.id,
        })
        sale_order.onchange_partner_id()
        sale_order.onchange_partner_shipping_id()
        # rewrite the user as the onchange_partner_id erases it
        sale_order.write({'user_id': self.project_id.user_id.id})
        sale_order.onchange_user_id()

        # create the sale lines, the map (optional), and assign existing timesheet to sale lines
        self._make_billable(sale_order)

        # confirm SO
        sale_order.action_confirm()
        return sale_order

    def _make_billable(self, sale_order):
        if self.pricing_type == 'fixed_rate':
            self._make_billable_at_project_rate(sale_order)
        else:
            self._make_billable_at_employee_rate(sale_order)

    def _make_billable_at_project_rate(self, sale_order):
        self.ensure_one()
        task_left = self.project_id.tasks.filtered(lambda task: not task.sale_line_id)
        ticket_timesheet_ids = self.env.context.get('ticket_timesheet_ids', [])
        for wizard_line in self.line_ids:
            task_ids = self.project_id.tasks.filtered(lambda task: not task.sale_line_id and task.timesheet_product_id == wizard_line.product_id)
            task_left -= task_ids
            # trying to simulate the SO line created a task, according to the product configuration
            # To avoid, generating a task when confirming the SO
            task_id = False
            if task_ids and wizard_line.product_id.service_tracking in ['task_in_project', 'task_global_project']:
                task_id = task_ids.ids[0]

            # create SO line
            sale_order_line = self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': wizard_line.product_id.id,
                'price_unit': wizard_line.price_unit,
                'project_id': self.project_id.id,  # prevent to re-create a project on confirmation
                'task_id': task_id,
                'product_uom_qty': 0.0,
            })

            if ticket_timesheet_ids and not self.project_id.sale_line_id and not task_ids:
                # With pricing = "project rate" in project. When the user wants to create a sale order from a ticket in helpdesk
                # The project cannot contain any tasks. Thus, we need to give the first sale_order_line created to link
                # the timesheet to this first sale order line.
                # link the project to the SO line
                self.project_id.write({
                    'sale_order_id': sale_order.id,
                    'sale_line_id': sale_order_line.id,
                    'partner_id': self.partner_id.id,
                })

            # link the tasks to the SO line
            task_ids.write({
                'sale_line_id': sale_order_line.id,
                'partner_id': sale_order.partner_id.id,
                'email_from': sale_order.partner_id.email,
            })

            # assign SOL to timesheets
            search_domain = [('task_id', 'in', task_ids.ids), ('so_line', '=', False), ('non_billable', '=', False)]
            if ticket_timesheet_ids:
                search_domain = [('id', 'in', ticket_timesheet_ids), ('so_line', '=', False)]

            self.env['account.analytic.line'].search(search_domain).write({
                'so_line': sale_order_line.id
            })
            sale_order_line.with_context({'no_update_planned_hours': True}).write({
                'product_uom_qty': sale_order_line.qty_delivered
            })

        if ticket_timesheet_ids and self.project_id.sale_line_id and not self.project_id.tasks and len(self.line_ids) > 1:
            # Then, we need to give to the project the last sale order line created
            self.project_id.write({
                'sale_line_id': sale_order_line.id
            })
        else:  # Otherwise, we are in the normal behaviour
            # link the project to the SO line
            self.project_id.write({
                'sale_order_id': sale_order.id,
                'sale_line_id': sale_order_line.id,  # we take the last sale_order_line created
                'partner_id': self.partner_id.id,
            })

        if task_left:
            task_left.sale_line_id = False

    def _make_billable_at_employee_rate(self, sale_order):
        # trying to simulate the SO line created a task, according to the product configuration
        # To avoid, generating a task when confirming the SO
        task_id = self.env['project.task'].search([('project_id', '=', self.project_id.id)], order='create_date DESC', limit=1).id
        project_id = self.project_id.id

        lines_already_present = dict([(l.employee_id.id, l) for l in self.project_id.sale_line_employee_ids])

        non_billable_tasks = self.project_id.tasks.filtered(lambda task: not task.sale_line_id)
        non_allow_billable_tasks = self.project_id.tasks.filtered(lambda task: task.non_allow_billable)

        map_entries = self.env['project.sale.line.employee.map']
        EmployeeMap = self.env['project.sale.line.employee.map'].sudo()

        # create SO lines: create on SOL per product/price. So many employee can be linked to the same SOL
        map_product_price_sol = {}  # (product_id, price) --> SOL
        for wizard_line in self.line_ids:
            map_key = (wizard_line.product_id.id, wizard_line.price_unit)
            if map_key not in map_product_price_sol:
                values = {
                    'order_id': sale_order.id,
                    'product_id': wizard_line.product_id.id,
                    'price_unit': wizard_line.price_unit,
                    'product_uom_qty': 0.0,
                }
                if wizard_line.product_id.service_tracking in ['task_in_project', 'task_global_project']:
                    values['task_id'] = task_id
                if wizard_line.product_id.service_tracking in ['task_in_project', 'project_only']:
                    values['project_id'] = project_id

                sale_order_line = self.env['sale.order.line'].create(values)
                map_product_price_sol[map_key] = sale_order_line

            if wizard_line.employee_id.id not in lines_already_present:
                map_entries |= EmployeeMap.create({
                    'project_id': self.project_id.id,
                    'sale_line_id': map_product_price_sol[map_key].id,
                    'employee_id': wizard_line.employee_id.id,
                })
            else:
                map_entries |= lines_already_present[wizard_line.employee_id.id]
                lines_already_present[wizard_line.employee_id.id].write({
                    'sale_line_id': map_product_price_sol[map_key].id
                })

        # link the project to the SO
        self.project_id.write({
            'sale_order_id': sale_order.id,
            'sale_line_id': sale_order.order_line[0].id,
            'partner_id': self.partner_id.id,
        })
        non_billable_tasks.write({
            'partner_id': sale_order.partner_id.id,
            'email_from': sale_order.partner_id.email,
        })
        non_allow_billable_tasks.sale_line_id = False

        tasks = self.project_id.tasks.filtered(lambda t: not t.non_allow_billable)
        # assign SOL to timesheets
        for map_entry in map_entries:
            search_domain = [('employee_id', '=', map_entry.employee_id.id),
                             ('so_line', '=', False), ('non_billable', '=', False)
                             ]
            ticket_timesheet_ids = self.env.context.get('ticket_timesheet_ids', [])
            if ticket_timesheet_ids:
                search_domain.append(('id', 'in', ticket_timesheet_ids))
            else:
                search_domain.append(('task_id', 'in', tasks.ids))
            self.env['account.analytic.line'].search(search_domain).write({
                'so_line': map_entry.sale_line_id.id
            })
            map_entry.sale_line_id.with_context({'no_update_planned_hours': True}).write({
                'product_uom_qty': map_entry.sale_line_id.qty_delivered
            })

        return map_entries


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('analytic_line_ids.project_id', 'analytic_line_ids.non_allow_billable', 'project_id.pricing_type',
                 'project_id.bill_type', 'analytic_line_ids.non_billable')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        lines_by_timesheet = self.filtered(
            lambda sol: sol.qty_delivered_method == 'timesheet')
        domain = lines_by_timesheet._timesheet_compute_delivered_quantity_domain()
        mapping = lines_by_timesheet.sudo()._get_delivered_quantity_by_analytic(domain)
        for line in lines_by_timesheet:
            line.qty_delivered = mapping.get(line.id or line._origin.id, 0.0)

    def _timesheet_compute_delivered_quantity_domain(self):
        """ Hook for validated timesheet in additional module """
        return [('project_id', '!=', False), ('non_allow_billable', '=', False), ('non_billable', '=', False)]
