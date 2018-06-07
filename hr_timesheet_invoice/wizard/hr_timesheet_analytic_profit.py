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


class account_analytic_profit(models.TransientModel):
    _name = 'hr.timesheet.analytic.profit'
    _description = 'Print Timesheet Profit'

    date_from = fields.Date(string='From', required=True, default=lambda *a : fields.Date.today()[:8]+'01')
    date_to = fields.Date(string='To', required=True, default=lambda *a : fields.Date.today())
    #~ journal_ids = fields.Many2many(comodel_name='account.analytic.journal', relation='analytic_profit_journal_rel', column1='analytic_id', column2='journal_id', string='Journal', required=True)
    employee_ids = fields.Many2many(comodel_name='res.users', relation='analytic_profit_emp_rel', column1='analytic_id', column2='emp_id', string='User', required=True)

    @api.multi
    def print_report(self):
        data = {}
        data['form'] = self.read()[0]
        ids_chk = self.env['account.analytic.line'].search([
                ('date', '>=', data['form']['date_from']),
                ('date', '<=', data['form']['date_to']),
                #~ ('journal_id', 'in', data['form']['journal_ids']),
                ('user_id', 'in', data['form']['employee_ids']),
                ])
        if not ids_chk:
            raise Warning(_('No record(s) found for this report.'))

        #~ data['form']['journal_ids'] = [(6, 0, data['form']['journal_ids'])] # Improve me => Change the rml/sxw so that it can support withou [0][2]
        data['form']['employee_ids'] = [(6, 0, data['form']['employee_ids'])]
        datas = {
            'ids': [],
            'model': 'account.analytic.line',
            'form': data['form']
        }
        return self.env['report'].get_action(
            [], 'hr_timesheet_invoice.report_analyticprofit', data=datas
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
