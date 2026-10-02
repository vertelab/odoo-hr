# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Mätning av beteende på en person (polymorf).

Varför polymorf och inte fyra fält på hr.employee: historiken är ett KRAV,
inte en finess. Metoden bygger på upprepade analyser som kalibreras över
tid. Fyra redigerbara tal direkt på personen skulle förstöra historiken
och göra det omöjligt att svara på när och av vem ett värde sattes.

Personens AKTUELLA värden lagras aldrig — de härleds från senaste
mätningen (samma mönster som hr.employee.skill.log).

Varför COPY och inte MOVE vid anställning: kandidatdata måste kunna
raderas enligt GDPR utan att den anställdes utvecklingshistorik förstörs.
"""

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# Modeller som en mätning får hänga på. Utökas av leverantörsmoduler
# eller när en kandidatabstraktion införs.
WORKSTYLE_RES_MODELS = [
    ('hr.employee', 'Employee'),
    ('hr.applicant', 'Applicant'),
]


class HrWorkstyleAssessment(models.Model):
    _name = 'hr.workstyle.assessment'
    _description = 'Behavioural Measurement'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread']

    res_model = fields.Selection(
        selection=WORKSTYLE_RES_MODELS, string='Applies To',
        required=True, index=True)
    res_id = fields.Many2oneReference(
        string='Record', model_field='res_model',
        required=True, index=True)
    res_name = fields.Char(
        string='Person', compute='_compute_res_name', store=False)

    date = fields.Date(
        string='Measurement Date', required=True, default=fields.Date.today,
        index=True)
    assessor_id = fields.Many2one(
        'hr.employee', string='Assessor',
        help="Handledaren som validerade mätningen i dialog med personen.")
    source = fields.Selection([
        ('recruitment', 'Recruitment'),
        ('development', 'Development'),
        ('followup', 'Follow-up'),
    ], string='Source', default='development', required=True)

    note = fields.Text(string='Note')

    copied_from_id = fields.Many2one(
        'hr.workstyle.assessment', string='Copied From',
        ondelete='set null', index=True,
        help="Ursprungsmätningen när en kandidats mätning kopieras till "
             "en anställd vid anställning. Nollas om ursprunget raderas, "
             "så att GDPR-radering inte blockerar.")

    line_ids = fields.One2many(
        'hr.workstyle.assessment.line', 'assessment_id',
        string='Scores', copy=True)

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for assessment in self:
            assessment.res_name = False
            if assessment.res_model and assessment.res_id:
                record = self.env[assessment.res_model].browse(
                    assessment.res_id).exists()
                if record:
                    assessment.res_name = record.display_name

    @api.constrains('res_model', 'res_id')
    def _check_res_id(self):
        for assessment in self:
            if not assessment.res_id:
                raise ValidationError("En mätning måste kopplas till en person.")

    @api.depends('res_model', 'res_id', 'date')
    def _compute_display_name(self):
        """Odoo 18: name_get är borttaget — använd _compute_display_name."""
        for assessment in self:
            if not assessment.id:
                assessment.display_name = ''
                continue
            assessment.display_name = "%s — %s" % (
                assessment.res_name or '?', assessment.date or '')


class HrWorkstyleAssessmentLine(models.Model):
    _name = 'hr.workstyle.assessment.line'
    _description = 'Behavioural Measurement Score'
    _order = 'rank, style_id'

    assessment_id = fields.Many2one(
        'hr.workstyle.assessment', string='Measurement', required=True,
        ondelete='cascade', index=True)
    style_id = fields.Many2one(
        'hr.workstyle.style', string='Behavioural Style', required=True,
        ondelete='restrict', index=True)
    score = fields.Integer(string='Score')

    scale_min = fields.Integer(related='style_id.scale_min', string='Scale Min')
    scale_max = fields.Integer(related='style_id.scale_max', string='Scale Max')

    rank = fields.Integer(
        string='Rank', compute='_compute_rank', store=True,
        help="1 = starkaste stilen i mätningen.")

    date = fields.Date(
        related='assessment_id.date', string='Measurement Date', store=True)

    _sql_constraints = [
        ('assessment_style_uniq', 'unique(assessment_id, style_id)',
         "En stil kan bara ha en poäng per mätning."),
    ]

    @api.constrains('score', 'style_id')
    def _check_score(self):
        for line in self:
            # Tomt score = omätt, inte noll. Tillåts medvetet.
            if not line.score:
                continue
            if line.score < line.style_id.scale_min \
                    or line.score > line.style_id.scale_max:
                raise ValidationError(
                    "Poängen %s ligger utanför skalans %s-%s för stilen %s."
                    % (line.score, line.style_id.scale_min,
                       line.style_id.scale_max, line.style_id.name))

    @api.depends('score', 'assessment_id.line_ids.score')
    def _compute_rank(self):
        for assessment in self.mapped('assessment_id'):
            lines = assessment.line_ids.filtered('score').sorted(
                key=lambda l: -l.score)
            for index, line in enumerate(lines, start=1):
                line.rank = index
            for line in assessment.line_ids - lines:
                line.rank = 0
