# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class Applicant(models.Model):

    _inherit = 'hr.applicant'

    def website_form_input_filter(self, request, values):
        values = super(Applicant, self).website_form_input_filter(request, values)
        _logger.warning(values)
        if 'partner_name' in values:
            values['name'] = _("%s's Ansökande") % values['partner_name']
        _logger.warning(values)
        return values