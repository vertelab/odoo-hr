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

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

#
# Create an final invoice based on selected timesheet lines
#

#
# TODO: check unit of measure !!!
#
class final_invoice_create(models.TransientModel):
    _name = 'hr.timesheet.invoice.create.final'
    _description = 'Create invoice from timesheet final'

    date = fields.Boolean(string='Date', help='Display date in the history of works')
    time = fields.Boolean(string='Time Spent', help='Display time in the history of works')
    name = fields.Boolean(string='Log of Activity', help='Display detail of work in the invoice line.')
    price = fields.Boolean(string='Cost', help='Display cost of the item you reinvoice')
    product = fields.Many2one(comodel_name='product.product', string='Product', help='The product that will be used to invoice the remaining amount')

    @api.multi
    def do_create(self):
        data = self.read()[0]
        # hack for fixing small issue (context should not propagate implicitly between actions)
        if 'default_type' in self._context:
            del self._context['default_type']
        self.env['account.analytic.line'].search([('invoice_id','=',False),('to_invoice','<>', False), ('id', 'in', self._context['active_ids'])]).invoice_cost_create(data)
        mod_ids = self.env['ir.model.data'].search([('name', '=', 'action_invoice_tree1')])
        res_id = mod_ids.read(['res_id'])[0]['res_id']
        act_win = self.env['ir.actions.act_window'].read([res_id]).read()[0]
        act_win['domain'] = [('id','in',[i.id for i in invs]),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
