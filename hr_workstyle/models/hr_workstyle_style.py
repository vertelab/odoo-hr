# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Beteendestilar — katalogen.

Färg, namn och lokal benämning är DATA, inte logik. En leverantörs
ordval (t.ex. färg-DISC:s röd/gul/grön/blå) sätts av leverantörsmodulen
(`hr_key_behaviour`), aldrig här. Det gör den generiska modellen
användbar med en annan leverantör eller med egen skattning.

Skalan (min/max) är också konfiguration: DISC-mätningar uttrycks ofta
1-10, men inget hindrar en annan skala.
"""

from odoo import api, fields, models
from odoo.exceptions import ValidationError

DEFAULT_SCALE_MIN = 1
DEFAULT_SCALE_MAX = 10


class HrWorkstyleStyle(models.Model):
    _name = 'hr.workstyle.style'
    _description = 'Behavioural Style'
    _order = 'sequence, id'

    name = fields.Char(
        string='Name', required=True, translate=True,
        help="Neutralt namn på stilen, t.ex. 'Dominant'.")
    code = fields.Char(
        string='Code', required=True, index=True,
        help="Kort kod, t.ex. D, I, S eller C.")
    local_name = fields.Char(
        string='Local Name',
        help="Kundens eller leverantörens ordval, t.ex. en färg. "
             "Lämnas tom i den generiska modulen.")
    color = fields.Char(
        string='Colour',
        help="Visningsfärg som hex-kod, t.ex. '#D32F2F'. Är data — "
             "sätts av leverantörsmodulen eller av en administratör.")
    description = fields.Text(
        string='Description',
        help="Beskrivning av beteendet, inte av personen.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Skalan är gemensam för katalogen — den beskriver hur stilar mäts.
    scale_min = fields.Integer(
        string='Scale Minimum', default=DEFAULT_SCALE_MIN, required=True,
        help="Lägsta möjliga poäng för en stil.")
    scale_max = fields.Integer(
        string='Scale Maximum', default=DEFAULT_SCALE_MAX, required=True,
        help="Högsta möjliga poäng för en stil.")

    line_ids = fields.One2many(
        'hr.job.workstyle.line', 'style_id', string='Job Requirements',
        help="Tjänsters kravprofiler som använder denna stil.")
    assessment_line_ids = fields.One2many(
        'hr.workstyle.assessment.line', 'style_id', string='Measurements')

    display_name_full = fields.Char(
        string='Display Name', compute='_compute_display_name_full')

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
         "Koden för en beteendestil måste vara unik."),
    ]

    @api.constrains('scale_min', 'scale_max')
    def _check_scale(self):
        for style in self:
            if style.scale_min >= style.scale_max:
                raise ValidationError(
                    "Skalans minimum (%s) måste vara lägre än maximum (%s)."
                    % (style.scale_min, style.scale_max))

    @api.depends('name', 'local_name', 'code')
    def _compute_display_name(self):
        """Odoo 18: name_get är borttaget — använd _compute_display_name."""
        for style in self:
            if not style.id:
                style.display_name = style.name or ''
                continue
            label = style.name or ''
            if style.local_name:
                label = "%s (%s)" % (label, style.local_name)
            style.display_name = label

    @api.depends('name', 'local_name', 'code')
    def _compute_display_name_full(self):
        for style in self:
            parts = [style.name or '']
            if style.local_name:
                parts.append(style.local_name)
            if style.code:
                parts.append("[%s]" % style.code)
            style.display_name_full = " — ".join(parts)
