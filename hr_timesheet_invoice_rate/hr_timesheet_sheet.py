# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from datetime import datetime, timedelta
import time
import re

import logging
_logger = logging.getLogger(__name__)

class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"
    @api.one
    def _invoice_rate(self):
        invoice_hours = 0.0
        for line in self.timesheet_ids:
            #raise Warning(line.to_invoice)
            invoice_hours += line.unit_amount * float(100.0 - line.to_invoice.factor) / 100.0
        self.invoice_hours = invoice_hours
        if self.total_attendance > 0.0:
            self.invoice_rate = invoice_hours / self.total_attendance * 100.0
            #~ raise Warning(invoice_hours / self.total_timesheet * 100.0,self.invoice_rate,self.total_timesheet > 0.0,invoice_hours, self.invoice_hours, self.total_timesheet)
    invoice_rate = fields.Float(string="Invoice Rate",compute="_invoice_rate")
    invoice_hours = fields.Float(string="Invoice Hours",compute="_invoice_rate")

