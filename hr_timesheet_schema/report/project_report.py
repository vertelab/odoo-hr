# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ReportProjectTaskUser(models.Model):
    _inherit = "account.analytic.line"

    schema_time = fields.Float('Schema Time', group_operator='avg', readonly=True)

    def _select(self):
        return super(ReportProjectTaskUser, self)._select() + """,
            schema_time as schema_time"""
            # ~ t.effective_hours as hours_effective,
            # ~ t.planned_hours - t.effective_hours - t.subtask_effective_hours as remaining_hours,
            # ~ planned_hours as hours_planned"""

    # ~ def _group_by(self):
        # ~ return super(ReportProjectTaskUser, self)._group_by() + """,
            # ~ remaining_hours,
            # ~ t.effective_hours,
            # ~ progress,
            # ~ planned_hours
            # ~ """
