# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Leverantörens rationale-vokabulär — återanvändbara motiv på kravrader.

Fritext accepteras fortfarande; vokabulären är ett erbjudande, inte ett krav.
"""

from odoo import fields, models


class HrKeyRationale(models.Model):
    _name = 'hr.key.rationale'
    _description = 'KEY Requirement Rationale'
    _order = 'sequence, name'

    name = fields.Char(string='Rationale', required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
