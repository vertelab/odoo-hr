# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrJobWorkstyleLine(models.Model):
    _inherit = 'hr.job.workstyle.line'

    rationale_id = fields.Many2one(
        'hr.key.rationale', string='Standard Rationale',
        help="Välj ett återanvändbart motiv. Fritext i 'Rationale' "
             "accepteras fortfarande och används när inget passar.")
