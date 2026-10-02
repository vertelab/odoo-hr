# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Analystyp och handledarvalidering — leverantörens begrepp.

KEY skiljer på fyra analyser:

    Individ  — självskattning som valideras i öppen dialog med en handledare.
               Upprepade analyser spårar och kalibrerar utveckling.
    Roll     — optimala beteenden inför rekrytering eller skapande av roll.
    360º     — självskattning + feedback från sex andra personer.
    Team     — individuella profiler jämförda med gruppens.

Analystypen är data (en post per typ), inte en hårdkodad Selection — en
leverantör kan ha andra namn eller fler typer.
"""

from odoo import api, fields, models


class HrKeyAnalysisType(models.Model):
    _name = 'hr.key.analysis.type'
    _description = 'KEY Analysis Type'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    # Beteendet som skiljer typerna åt — data, inte logik i koden.
    applies_to_person = fields.Boolean(
        string='Measures a Person', default=True,
        help="False för Roll-analys, som beskriver en rolls förväntade "
             "beteende snarare än en persons.")
    has_feedback_providers = fields.Boolean(
        string='Collects Feedback From Others', default=False,
        help="True för 360°-analys.")
    measures_group = fields.Boolean(
        string='Measures a Group', default=False,
        help="True för Team-analys.")

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
         "Koden för en analystyp måste vara unik."),
    ]


class HrWorkstyleAssessment(models.Model):
    _inherit = 'hr.workstyle.assessment'

    analysis_type_id = fields.Many2one(
        'hr.key.analysis.type', string='Analysis Type',
        help="Vilken av KEY:s analyser mätningen kommer från.")

    feedback_provider_count = fields.Integer(
        string='Feedback Providers',
        help="Antal personer som gett feedback utöver självskattningen. "
             "Endast ANTALET lagras — aldrig deras identiteter i poängen.")

    validated = fields.Boolean(
        string='Validated', tracking=True,
        help="Mätningen är validerad i dialog med en handledare.")
    validation_date = fields.Date(string='Validated On')

    def action_mark_validated(self):
        for assessment in self:
            assessment.write({
                'validated': True,
                'validation_date': fields.Date.today(),
            })
