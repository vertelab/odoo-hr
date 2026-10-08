# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
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

VARFÖR ETT REFERENCE-FÄLT OCH INTE res_model + res_id
----------------------------------------------------
Den första versionen använde `res_model` (Selection) + `res_id`
(Many2oneReference) — samma mönster som `mail.message`. Det fungerar för
mail eftersom posting alltid sker via en känd tråd. För en mätning som
skapas MANUELLT i UI:t är mönstret trasigt:

  * `res_id` är `Many2oneReference`. Den enda widget Odoo har för den
    typen är `many2one_reference_integer` — ett rent heltalsfält. Det
    finns alltså ingen persondropdown att välja i.
  * Fältet var dessutom `invisible="1"` i formuläret, så `res_id`
    förblev alltid NULL. Eftersom det är `required=True` (NOT NULL i
    databasen) kraschade varje ny post med
    `NotNullViolation: null value in column "res_id"`.

`fields.Reference` lagrar både modell och id i ETT värde
('hr.employee,42') och renderas som en riktig mång2ett-widget med
modellväljare. Det är den inbyggda lösningen på exakt detta problem.

Odoo säger det själv i fields.py (One2many.setup_nonrelated):

    # setting one2many fields only invalidates many2one inverses;
    # integer inverses (res_model/res_id pairs) are not supported

Därför lägger `mail.message` heller aldrig sina polymorfa dokument som
en invers One2many — och därför gör inte den här modellen det. Alla
uppslag sker mot det enda `person_ref`-värdet.
"""

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# Modeller som en mätning får hänga på. Leverantörsmoduler utökar listan
# via `_workstyle_person_models()` hellre än att redigera den här filen.
WORKSTYLE_RES_MODELS = [
    ('hr.employee', 'Employee'),
    ('hr.applicant', 'Applicant'),
]


class HrWorkstyleAssessment(models.Model):
    _name = 'hr.workstyle.assessment'
    _description = 'Behavioural Measurement'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread']

    # ── Personen ───────────────────────────────────────────────────────
    #
    # ETT fält som bär både modell och id ('hr.employee,42'). Detta är
    # sanningen om vem mätningen gäller.
    person_ref = fields.Reference(
        string='Person', selection='_workstyle_person_models',
        required=True, index=True,
        help="Anställd eller kandidat som mätningen gäller.")

    @api.model
    def _workstyle_person_models(self):
        """Modeller en mätning kan kopplas till.

        En metod (inte en hårdkodad Selection) så att leverantörsmoduler
        kan utöka listan utan att redigera den här filen.
        """
        return list(WORKSTYLE_RES_MODELS)

    # Läsvänliga speglingar av person_ref — uttryckligen INTE lagrade och
    # INTE skrivbara. person_ref är enda sanningen; de här finns så att
    # läsare (och domäner) slipper parsa strängen.
    person_model = fields.Char(
        string='Applies To', compute='_compute_person_model')
    person_res_id = fields.Integer(
        string='Record ID', compute='_compute_person_res_id')

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

    # ── Cache-invalidering ───────────────────────────────────────────
    #
    # hr.employee.workstyle_assessment_ids är ett icke-lagrat compute-fält
    # (Odoo kan inte invertera en One2many över ett polymorft Reference —
    # se filhuvudet). Ett sådant fält invalideras INTE automatiskt på
    # personen när en mätning skapas här, eftersom det inte finns någon
    # depends-kedja mellan modellerna. Utan detta står personens cachade
    # värden still inom samma transaktion — vilket slår både i tester och
    # i all kod som skapar en mätning och sedan läser personen.
    #
    # (I en web-förfrågan märks det inte: varje request har en ny cache.
    # Det är därför felet bara syns i tester och i shell.)
    def _invalidate_person_cache(self):
        """Nollställ personens arbetsstilsfält efter en mätningsändring.

        behavioural_match och matching_score är LAGRADE compute-fält som
        beror på workstyle_latest_id — vilket i sin tur är ICKE-LAGRAT.
        Ett lagrat fält rekomputeras inte av en ren cache-invalidering: en
        invalidering tömmer cachen men rör inte DB-värdet, så det lagrade
        fältet står kvar på sitt gamla värde. `modified()` är rätt API —
        det markerar fältet för omräkning OCH persisterar resultatet.

        (Tidigare användes invalidate_recordset, vilket tyst lämnade
        gaugerna på 0 i databasen och gjorde dem osorterbara.)
        """
        for assessment in self:
            person = assessment.person_ref
            if person and 'workstyle_assessment_ids' in person._fields:
                person.modified([
                    'workstyle_latest_id',
                    'behavioural_match',
                    'matching_score',
                ])
                person.invalidate_recordset([
                    'workstyle_assessment_ids',
                    'workstyle_assessment_count',
                    'workstyle_d_latest',
                    'workstyle_i_latest',
                    'workstyle_s_latest',
                    'workstyle_c_latest',
                    'workstyle_gap_ids',
                ])

    @api.model
    def _set_person_score(self, res_model, res_id, code, value):
        """Sätt poängen för en stil genom att skapa en NY mätning.

        Anropas av inversen på workstyle_d/i/s/c_latest. Varje ändring i
        formuläret skapar en ny mätning daterad idag — historiken är
        avsiktlig (produktägarbeslut 2026-10-05), inte en bieffekt.

        Poängen för de ANDRA stilarna bärs vidare från den senaste
        mätningen, så att en ny mätning alltid är en komplett profil och
        inte tappar stilar man inte rörde. `value` 0/falskt utelämnar
        stilen — omätt är inte noll.
        """
        person_ref = '%s,%s' % (res_model, res_id)
        style = self.env['hr.workstyle.style'].search(
            [('code', '=', code)], limit=1)
        if not style:
            return

        previous = self.search(
            [('person_ref', '=', person_ref)],
            order='date desc, id desc', limit=1)
        scores = {}
        if previous:
            scores = {line.style_id.id: line.score
                      for line in previous.line_ids}
        if value:
            scores[style.id] = value
        else:
            scores.pop(style.id, None)

        if not scores:
            # Allt tomt — ingen mätning att skapa.
            return
        self.create({
            'person_ref': person_ref,
            'source': 'development',
            'line_ids': [(0, 0, {'style_id': style_id, 'score': score})
                         for style_id, score in scores.items()],
        })

    @api.model_create_multi
    def create(self, vals_list):
        assessments = super().create(vals_list)
        assessments._invalidate_person_cache()
        return assessments

    def write(self, vals):
        result = super().write(vals)
        # person_ref kan ha bytts, och då måste både den gamla och den nya
        # personens cache nollas.
        self._invalidate_person_cache()
        return result

    def unlink(self):
        persons = self.mapped('person_ref')
        result = super().unlink()
        for person in persons:
            if 'workstyle_assessment_ids' in person._fields:
                person.invalidate_recordset()
        return result

    def _person_record(self):
        """Personen mätningen gäller, eller tomt recordset."""
        self.ensure_one()
        return self.person_ref if self.person_ref else self.env['hr.employee'].browse()

    @api.depends('person_ref')
    def _compute_person_model(self):
        for assessment in self:
            assessment.person_model = (
                assessment.person_ref._name if assessment.person_ref else False)

    @api.depends('person_ref')
    def _compute_person_res_id(self):
        for assessment in self:
            assessment.person_res_id = (
                assessment.person_ref.id if assessment.person_ref else False)

    @api.depends('person_ref', 'date')
    def _compute_display_name(self):
        """Odoo 18: name_get är borttaget — använd _compute_display_name."""
        for assessment in self:
            if not assessment.id:
                assessment.display_name = ''
                continue
            name = assessment.person_ref.display_name if assessment.person_ref else '?'
            assessment.display_name = "%s — %s" % (name, assessment.date or '')


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
