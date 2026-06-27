# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    onboarding_id = fields.Many2one('hr.onboarding', string="Onboarding",
                                     ondelete='set null')
    offboarding_id = fields.Many2one('hr.offboarding', string="Offboarding",
                                      ondelete='set null')
