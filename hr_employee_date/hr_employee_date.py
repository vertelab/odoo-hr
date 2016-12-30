# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
import time
import re

import logging
_logger = logging.getLogger(__name__)

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    date_start = fields.Char(string='Employed from', compute='_get_earliest_contract_date')

    @api.one
    def _get_earliest_contract_date(self):
        date = '2099-12-31'
        for c in self.sudo().contract_ids:
            if c.trial_date_start < date:
                date = c.trial_date_start
            if c.date_start < date:
                date = c.date_start
        if date == '2099-12-31':
            self.date_start = None
        else:
            self.date_start = date



