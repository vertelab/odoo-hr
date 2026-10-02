# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    workstyle_line_ids = fields.One2many(
        'hr.job.workstyle.line', 'job_id',
        string='Behavioural Profile', copy=True)

    workstyle_line_count = fields.Integer(
        string='Behavioural Requirements',
        compute='_compute_workstyle_line_count')

    @api.depends('workstyle_line_ids')
    def _compute_workstyle_line_count(self):
        for job in self:
            job.workstyle_line_count = len(job.workstyle_line_ids)
