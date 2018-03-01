# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _, exceptions
from odoo.exceptions import Warning
import time

import logging
_logger = logging.getLogger(__name__)


class hr_timesheet_invoice_factor(models.Model):
    _name = "hr_timesheet_invoice.factor"
    _description = "Invoice Rate"
    _order = 'factor'

    name = fields.Char(string='Internal Name', required=True, translate=True)
    customer_name = fields.Char(string='Name', help="Label for the customer")
    factor = fields.Float(string='Discount (%)', required=True, default=lambda *a: 0.0, help="Discount in percentage")


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    pricelist_id = fields.Many2one(comodel_name='product.pricelist', string='Pricelist',
        help="The product to invoice is defined on the employee form, the price will be deducted by this pricelist on the product.")
    amount_max = fields.Float(string='Max. Invoice Price',
        help="Keep empty if this contract is not limited to a total fixed price.")
    amount_invoiced = fields.Float(compute='_invoiced_calc', string='Invoiced Amount',
        help="Total invoiced")
    to_invoice = fields.Many2one(comodel_name='hr_timesheet_invoice.factor', string='Timesheet Invoicing Ratio',
        help="You usually invoice 100% of the timesheets. But if you mix fixed price and timesheet invoicing, you may use another ratio. For instance, if you do a 20% advance invoice (fixed price, based on a sales order), you should invoice the rest on timesheet with a 80% ratio.")

    @api.multi
    def _invoiced_calc(self, name, arg):
        res = {}

        #~ self.env.cr.execute('SELECT account_id as account_id, l.invoice_id '
                #~ 'FROM hr_analytic_timesheet h LEFT JOIN account_analytic_line l '
                    #~ 'ON (h.line_id=l.id) '
                    #~ 'WHERE l.account_id = ANY(%s)', (ids,))
        account_to_invoice_map = {}
        for rec in self.env.cr.dictfetchall():
            account_to_invoice_map.setdefault(rec['account_id'], []).append(rec['invoice_id'])

        for account in self:
            invoice_ids = filter(None, list(set(account_to_invoice_map.get(account.id, []))))
            for invoice in self.env['account.invoice'].browse(invoice_ids):
                res.setdefault(account.id, 0.0)
                res[account.id] += invoice.amount_untaxed
        for s in self:
            res[s.id] = round(res.get(s.id, 0.0),2)

        return res

    @api.multi
    def on_change_partner_id(self, partner_id, name):
        res = super(account_analytic_account, self).on_change_partner_id(partner_id, name)
        if partner_id:
            part = self.env['res.partner'].browse(partner_id)
            pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
            if pricelist:
                res['value']['pricelist_id'] = pricelist
        return res

    @api.multi
    def set_close(self):
        return self.write({'state': 'close'})

    @api.multi
    def set_cancel(self):
        return self.write({'state': 'cancelled'})

    @api.multi
    def set_open(self):
        return self.write({'state': 'open'})

    @api.multi
    def set_pending():
        return self.write({'state': 'pending'})


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    invoice_id = fields.Many2one(comodel_name='account.invoice', string='Invoice', ondelete="set null", copy=False)
    to_invoice = fields.Many2one(comodel_name='hr_timesheet_invoice.factor', string='Invoiceable', help="It allows to set the discount while making invoice, keep empty if the activities should not be invoiced.")

    # not exist in account in Odoo 10.0
    #~ @api.model
    #~ def _default_journal(self):
        #~ record_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        #~ if record_ids:
            #~ employee = self.env['hr.employee'].browse(record_ids[0])
            #~ return employee.journal_id and employee.journal_id.id or False
        #~ return False

    #~ @api.model
    #~ def _default_general_account(self):
        #~ record_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        #~ if record_ids:
            #~ employee = self.env['hr.employee'].browse(record_ids[0])
            #~ if employee.product_id and employee.product_id.property_account_income_id:
                #~ return employee.product_id.property_account_income_id.id
        #~ return False

    #~ _defaults = {
        #~ 'journal_id' : _default_journal,
        #~ 'general_account_id' : _default_general_account,
    #~ }

    @api.multi
    def write(self, vals):
        self._check_inv(vals)
        return super(account_analytic_line, self).write(vals)

    @api.multi
    def _check_inv(self, vals):
        select = self.mapped('id')
        if isinstance(select, (int, long)):
            select = [self.mapped('id')]
        if (not vals.has_key('invoice_id')) or vals['invoice_id' ] == False:
            for line in self.browse(select):
                if line.invoice_id:
                    raise Warning(_('You cannot modify an invoiced analytic line!'))
        return True

    @api.model
    def _get_invoice_price(self, account, product_id, user_id, qty):
        if account.pricelist_id:
            pl = account.pricelist_id.id
            price = self.env['product.pricelist'].price_get([pl], product_id, qty or 1.0, account.partner_id.id)[pl]
        else:
            price = 0.0
        return price

    @api.model
    def _prepare_cost_invoice(self, partner, company_id, currency_id, analytic_lines):
        """ returns values used to create main invoice from analytic lines"""
        invoice_name = analytic_lines[0].account_id.name

        date_due = False
        if partner.property_payment_term_id:
            pterm_list = partner.property_payment_term_id.compute(value=1, date_ref=fields.Date.today())
            if pterm_list:
                pterm_list = [line[0] for line in pterm_list]
                pterm_list.sort()
                date_due = pterm_list[-1][0]
        return {
            'name': "%s - %s" % (fields.Date.today(), invoice_name),
            'partner_id': partner.id,
            'company_id': company_id,
            'payment_term_id': partner.property_payment_term_id.id or False,
            'account_id': partner.property_account_receivable_id.id,
            'currency_id': currency_id,
            'date_due': date_due,
            'fiscal_position_id': partner.property_account_position_id.id
        }

    @api.model
    def _prepare_cost_invoice_line(self, product_id, uom, user_id, factor_id, account, analytic_lines, data):
        total_price = sum(l.amount for l in analytic_lines)
        if total_price == 0.0:
            for l in analytic_lines:
                l.amount = l.product_id.with_context(
                    partner=l.account_id.partner_id.id,
                    date_order=l.date,
                    pricelist=l.account_id.pricelist_id.id,
                    uom=l.product_uom_id.id
                ).price*l.unit_amount
            total_price = sum(l.amount for l in analytic_lines)
        total_qty = sum(l.unit_amount for l in analytic_lines)

        if data.get('product'):
            # force product, use its public price
            if isinstance(data['product'], (tuple, list)):
                product_id = data['product'][0]
            else:
                product_id = data['product']
            #~ unit_price = self.with_context(uom=uom)._get_invoice_price(account, product_id, user_id, total_qty)
            unit_price = self.env['product.product'].browse(product_id).with_context(
                partner=analytic_lines[0].account_id.partner_id.id,
                date_order=analytic_lines[0].date,
                pricelist=analytic_lines[0].account_id.pricelist_id.id,
                uom=analytic_lines[0].product_uom_id.id
            ).price

        #~ elif journal_type == 'general' and product_id:
            # timesheets, use sale price
            #~ unit_price = self.with_context(uom=uom)._get_invoice_price(account, product_id, user_id, total_qty)
        else:
            # expenses, using price from amount field
            unit_price = total_price*-1.0 / total_qty

        factor = self.env['hr_timesheet_invoice.factor'].with_context(uom=uom).browse(factor_id)
        factor_name = factor.customer_name or ''
        curr_invoice_line = {
            'price_unit': unit_price,
            'quantity': total_qty,
            'product_id': product_id,
            'discount': factor.factor,
            #~ 'invoice_id': invoice_id.id,
            'name': factor_name,
            #~ 'uos_id': uom,
            'account_analytic_id': account.id,
        }
        if product_id:
            product = self.env['product.product'].with_context(uom=uom).browse(product_id)
            factor_name = self.env['product.product'].with_context(uom=uom).browse(product_id).name_get()[0][1]
            if factor.customer_name:
                factor_name += ' - ' + factor.customer_name

            general_account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
            if not general_account:
                raise Warning(_('Error!'), _("Configuration Error!") + '\n' + _("Please define income account for product '%s'.") % product.name)
            taxes = product.taxes_id or general_account.tax_ids
            tax = self.env['account.fiscal.position'].map_tax(account.partner_id.property_account_position_id, taxes)
            if len(tax) == 0:
                tax = taxes
            curr_invoice_line.update({
                'invoice_line_tax_ids': [(6, 0, tax.mapped('id'))],
                'name': factor_name,
                'account_id': general_account.id,
            })

            note = []
            for line in analytic_lines:
                # set invoice_line_note
                details = []
                if data.get('date', False):
                    details.append(line['date'])
                if data.get('time', False):
                    if line['product_uom_id']:
                        details.append("%s %s" % (line.unit_amount, line.product_uom_id.name))
                    else:
                        details.append("%s" % (line['unit_amount'], ))
                if data.get('name', False):
                    details.append(line['name'])
                if details:
                    note.append(u' - '.join(map(lambda x: unicode(x) or '', details)))
            if note:
                curr_invoice_line['name'] += "\n" + ("\n".join(map(lambda x: unicode(x) or '', note)))
        return curr_invoice_line

    @api.multi
    def invoice_cost_create(self, data=None, separate_work_lines=False):
        invoices = []
        if data is None:
            data = {}

        # use key (partner/account, company, currency)
        # creates one invoice per key
        invoice_grouping = {}

        currency_id = False
        # prepare for iteration on journal and accounts
        for line in self:

            key = (line.account_id.id,
                   line.account_id.company_id.id,
                   line.account_id.pricelist_id.currency_id.id)
            invoice_grouping.setdefault(key, []).append(line)
        for (key_id, company_id, currency_id), analytic_lines in invoice_grouping.items():
            # key_id is an account.analytic.account
            account = analytic_lines[0].account_id
            partner = account.partner_id  # will be the same for every line
            if (not partner) or not (currency_id):
                raise Warning(_('Contract incomplete. Please fill in the Customer and Pricelist fields for %s.') % (account.name))

            curr_invoice = self._prepare_cost_invoice(partner, company_id, currency_id, analytic_lines)
            curr_invoice['invoice_line_ids'] = []

            # use key (product, uom, user, invoiceable, analytic account, journal type)
            # creates one invoice line per key
            invoice_lines_grouping = {}
            for analytic_line in analytic_lines:
                account = analytic_line.account_id

                if not analytic_line.to_invoice:
                    raise osv.except_osv(_('Error!'), _('Trying to invoice non invoiceable line for %s.') % (analytic_line.product_id.name))

                key = (analytic_line.product_id.id,
                       analytic_line.product_uom_id.id,
                       analytic_line.user_id.id,
                       analytic_line.to_invoice.id,
                       analytic_line.account_id)
                       #~ analytic_line.journal_id.type)
                # We want to retrieve the data in the partner language for the invoice creation
                analytic_line = self.env['account.analytic.line'].with_context(lang=partner.lang, force_company=company_id, company_id=company_id).browse([line.id for line in analytic_line])
                invoice_lines_grouping.setdefault(key, []).append(analytic_line)

            # finally creates the invoice line
            for (product_id, uom, user_id, factor_id, account), lines_to_invoice in invoice_lines_grouping.items():
                if separate_work_lines:
                    for line_to_invoice in lines_to_invoice:
                        curr_invoice_line = self.with_context(lang=partner.lang, force_company=company_id, company_id=company_id)._prepare_cost_invoice_line(
                            product_id, uom, user_id, factor_id, account, line_to_invoice, data)
                        curr_invoice['invoice_line_ids'].append((0,0,curr_invoice_line))
                else:
                    curr_invoice_line = self.with_context(lang=partner.lang, force_company=company_id, company_id=company_id)._prepare_cost_invoice_line(
                        product_id, uom, user_id, factor_id, account, lines_to_invoice, data)
                    curr_invoice['invoice_line_ids'].append((0,0,curr_invoice_line))
                #~ self.env['account.invoice.line'].create(curr_invoice_line)
            _logger.warn(curr_invoice)
            last_invoice = self.env['account.invoice'].with_context(lang=partner.lang, force_company=company_id, company_id=company_id).create(curr_invoice)
            last_invoice.compute_taxes()
            invoices.append(last_invoice)
            last_invoice.message_post_with_view('mail.message_origin_link',
                        values={'self': last_invoice, 'origin': analytic_lines[0]},
                        subtype_id=self.env.ref('mail.mt_note').id)
            for l in analytic_lines:
                l.invoice_id = last_invoice.id
        return invoices

    @api.multi
    @api.onchange('account_id')
    def on_change_account_id(self):
        res = {'value':{}}
        if not self.account_id:
            return res
        res.setdefault('value',{})
        acc = self.env['account.analytic.account'].browse(self.account_id.id)
        st = acc.to_invoice.id
        res['value']['to_invoice'] = st or False
        #~ if acc.state=='pending':
            #~ res['warning'] = {
                #~ 'title': _('Warning'),
                #~ 'message': _('The analytic account is in pending state.\nYou should not work on this account !')
            #~ }
        return res


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_analytic_lines(self):
        iml = super(account_invoice, self)._get_analytic_lines()

        if self[0].type == 'in_invoice':
            for il in iml:
                if il['account_analytic_id']:
            # *-* browse (or refactor to avoid read inside the loop)
                    to_invoice = self.env['account.analytic.account'].read([il['account_analytic_id']], ['to_invoice'])[0]['to_invoice']
                    if to_invoice:
                        il['analytic_lines'][0][2]['to_invoice'] = to_invoice[0]
        return iml


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create_analytic_lines(self):
        res = super(account_move_line, self).create_analytic_lines()
        for move_line in self:
            #For customer invoice, link analytic line to the invoice so it is not proposed for invoicing in Bill Tasks Work
            invoice_id = move_line.invoice_id and move_line.invoice_id.type in ('out_invoice','out_refund') and move_line.invoice_id.id or False
            for line in move_line.analytic_line_ids:
                line.env['account.analytic.line'].write({
                    'invoice_id': invoice_id,
                    'to_invoice': line.account_id.to_invoice and line.account_id.to_invoice.id or False
                })
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
