# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Tjänstens kravprofil — ett INTERVALL per beteendestil.

Varför intervall och inte ett enda tal: en roll har ett spann av beteenden
som fungerar. Både under OCH över spannet är information — en VD med
maximalt C kan lida av analysförlamning. Därför är den övre gränsen
obligatorisk; utan den blir avvikelsen uppåt osynlig.

`rationale` bär motivet ("förankrar beslut innan de implementeras").
En abstrakt förmåga kan bäras av flera stilar (S för människorna, C för
underlaget) — därför beskriver raden STILEN och rationale VARFÖR.
"""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrJobWorkstyleLine(models.Model):
    _name = 'hr.job.workstyle.line'
    _description = 'Job Behavioural Requirement'
    _order = 'sequence, id'

    job_id = fields.Many2one(
        'hr.job', string='Job Position', required=True,
        ondelete='cascade', index=True)
    style_id = fields.Many2one(
        'hr.workstyle.style', string='Behavioural Style', required=True,
        ondelete='restrict', index=True)

    # INGA defaults här. En default på ideal_max skulle göra att
    # required=True aldrig utlöses — och kravet "utan övre gräns blir
    # avvikelsen uppåt osynlig" skulle tyst upphöra att gälla.
    ideal_min = fields.Integer(string='From', required=True)
    ideal_max = fields.Integer(string='To', required=True)

    importance = fields.Selection([
        ('nice_to_have', 'Nice to have'),
        ('important', 'Important'),
        ('critical', 'Critical'),
    ], string='Importance', default='important', required=True,
        help="Etikett i denna version — påverkar inte gap-beräkningen.")

    rationale = fields.Text(
        string='Rationale',
        help="Varför rollen förväntar sig detta beteende, t.ex. "
             "'förankrar beslut innan de implementeras'.")

    sequence = fields.Integer(default=10)

    # Skalan kommer från stilen — en enda sanning om hur poäng tolkas.
    scale_min = fields.Integer(related='style_id.scale_min', string='Scale Min')
    scale_max = fields.Integer(related='style_id.scale_max', string='Scale Max')

    company_id = fields.Many2one(
        related='job_id.company_id', string='Company', store=True)

    _sql_constraints = [
        ('job_style_uniq', 'unique(job_id, style_id)',
         "En tjänst kan bara ha ett krav per beteendestil."),
    ]

    @api.constrains('ideal_min', 'ideal_max')
    def _check_range(self):
        for line in self:
            if line.ideal_max < line.ideal_min:
                raise ValidationError(
                    "Den övre gränsen (%s) får inte vara lägre än den nedre "
                    "gränsen (%s)." % (line.ideal_max, line.ideal_min))

    @api.constrains('ideal_min', 'ideal_max', 'style_id')
    def _check_scale_bounds(self):
        for line in self:
            if line.ideal_min < line.style_id.scale_min \
                    or line.ideal_max > line.style_id.scale_max:
                raise ValidationError(
                    "Intervallet %s-%s ligger utanför skalans %s-%s för "
                    "stilen %s."
                    % (line.ideal_min, line.ideal_max,
                       line.style_id.scale_min, line.style_id.scale_max,
                       line.style_id.name))
