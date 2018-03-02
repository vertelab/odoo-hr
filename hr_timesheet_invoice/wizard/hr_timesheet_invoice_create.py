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
from odoo import api, fields, models, _
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class hr_timesheet_invoice_create(models.TransientModel):
    _name = 'hr.timesheet.invoice.create'
    _description = 'Create invoice from timesheet'

    date = fields.Boolean(string='Date', default=True, help='The real date of each work will be displayed on the invoice')
    time = fields.Boolean(string='Time spent', help='The time of each work done will be displayed on the invoice')
    name = fields.Boolean(string='Description', default=True, help='The detail of each work done will be displayed on the invoice')
    price = fields.Boolean(string='Cost', help='The cost of each work done will be displayed on the invoice. You probably don\'t want to check this')
    product = fields.Many2one(comodel_name='product.product', string='Force Product', help='Fill this field only if you want to force to use a specific product. Keep empty to use the real product that comes from the cost.')
    separate_work_lines = fields.Boolean(string='Separate Work Lines')

    #~ @api.multi
    #~ def view_init(self, fields):
        #~ """
        #~ This function checks for precondition before wizard executes
        #~ @param self: The object pointer
        #~ @param cr: the current row, from the database cursor,
        #~ @param uid: the current user’s ID for security checks,
        #~ @param fields: List of fields for default value
        #~ @param context: A standard dictionary for contextual values
        #~ """
        #~ for analytic in self.env['account.analytic.line'].browse(self.env.context.get('active_ids', [])).filtered(lambda l: not l.invoice_id):
            #~ if analytic.invoice_id:
                #~ raise Warning(_("Invoice is already linked to some of the analytic line(s)!"))

    @api.multi
    def do_create(self):
        data = self.read()[0]
        # Create an invoice based on selected timesheet lines
        ids = self.env['account.analytic.line'].search([('invoice_id', '=' ,False), ('to_invoice', '<>', False), ('id', 'in', self._context['active_ids'])]).filtered(lambda l: not l.invoice_id)
        if len(ids) > 0:
            invs = ids.invoice_cost_create(data, self.separate_work_lines)
        else:
            invs = self.env['account.analytic.line'].browse()
        mod_ids = self.env['ir.model.data'].search([('name', '=', 'action_invoice_tree1')])
        res_id = mod_ids.read(['res_id'])[0]['res_id']
        act_win = self.env['ir.actions.act_window'].browse(res_id).read()[0]
        act_win['domain'] = [('id','in',[i.id for i in invs]),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

