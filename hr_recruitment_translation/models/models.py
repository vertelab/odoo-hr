# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Applicant(models.Model):

    _inherit = 'hr.applicant'

    def website_form_input_filter(self, request, values):
        if 'partner_name' in values:
            values.setdefault('name', _('%s\'s Application') % values['partner_name'])
        return values