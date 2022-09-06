# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2022 Vertel AB (<http://vertel.se>).
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

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
import logging
_logger = logging.getLogger(__name__)

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    def _get_expense_account_destination(self):
        self.ensure_one()
        account_dest = self.env['account.account']
        if self.payment_mode == 'company_account':
            if not self.sheet_id.bank_journal_id.payment_credit_account_id:
                raise UserError(_("No Outstanding Payments Account found for the %s journal, please configure one.") % (self.sheet_id.bank_journal_id.name))
            account_dest = self.sheet_id.bank_journal_id.payment_credit_account_id.id
        elif self.sheet_id and self.sheet_id.journal_id and self.sheet_id.journal_id.payable_account:
            _logger.warning(f"THE JOURNAL HAD A PAYABLE ACCOUNT {self.sheet_id.journal_id.payable_account.code}")
            return self.sheet_id.journal_id.payable_account.id
        else:
            if not self.employee_id.sudo().address_home_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (self.employee_id.name))
            partner = self.employee_id.sudo().address_home_id.with_company(self.company_id)
            account_dest = partner.property_account_payable_id.id or partner.parent_id.property_account_payable_id.id
        return account_dest
