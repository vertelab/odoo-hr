# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Mätningar på hr.employee — och de HÄRLEDDA aktuella värdena.

De aktuella värdena är compute-fält, aldrig lagrad sanning. Sanningen är
mätningen (hr.workstyle.assessment). Detta är samma mönster som
hr.employee.skill.log: aktuellt värde = senaste historikposten.
"""

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Compute, inte invers One2many. Odoo kan inte invertera en One2many
    # över ett polymorft Reference-fält — se filhuvudet i
    # hr_workstyle_assessment.py. Två saker måste då lösas manuellt:
    #
    #   1. Fältet måste vara SÖKBART. Ett icke-lagrat fält utan search-
    #      metod ger en TYST tom domän — osv/expression.py loggar
    #      "Non-stored field ... cannot be searched" och släpper lövbladet.
    #      All kod som filtrerar på workstyle_assessment_ids hade alltså
    #      fått fel svar utan ett felmeddelande.
    #   2. Cachen måste INVALIDERAS när en mätning skapas, ändras eller
    #      raderas. Ett @api.depends('id') är värdelöst: id ändras aldrig,
    #      så fältet räknas om en gång och står sedan still.
    #
    # Båda löses med en search-metod och ett depends mot mätningens
    # person_ref.
    workstyle_assessment_ids = fields.One2many(
        'hr.workstyle.assessment',
        compute='_compute_workstyle_assessment_ids',
        search='_search_workstyle_assessment_ids',
        string='Behavioural Measurements')

    def _compute_workstyle_assessment_ids(self):
        Assessment = self.env['hr.workstyle.assessment']
        for employee in self:
            employee.workstyle_assessment_ids = Assessment.search([
                ('person_ref', '=', 'hr.employee,%s' % employee.id)],
                order='date desc, id desc')

    def _search_workstyle_assessment_ids(self, operator, value):
        """Översätt en domän på fältet till ett filter på hr.employee.

        Fältet är ett polymorft Reference — Odoo kan inte bygga en invers
        själv. Utan den här metoden blir varje domän på fältet tyst tom
        (osv/expression.py loggar bara en varning och släpper lövbladet).

        `value` är MÄTNINGS-id:n (modellen på andra sidan relationen),
        inte person-id:n. Vi letar därför upp mätningarna och plockar ut
        deras personer.
        """
        Assessment = self.env['hr.workstyle.assessment']

        if value is False:
            # 'har ingen mätning' / 'har någon mätning'. Även här ger
            # mapped() på ett Reference-fält en LISTA — plocka id per post.
            found = Assessment.search(
                [('person_ref', '=like', 'hr.employee,%')])
            ids = [a.person_ref.id for a in found if a.person_ref]
            return [('id', 'in' if operator in ('!=', 'not in') else 'not in', ids)]

        identifiers = value if isinstance(value, list) else [value]
        assessments = Assessment.search([('id', operator, identifiers)])
        # mapped() på ett Reference-fält ger en LISTA av recordsets —
        # inte ett recordset. Plocka ut id:na per post i stället.
        person_ids = [
            a.person_ref.id for a in assessments
            if a.person_ref and a.person_ref._name == 'hr.employee']
        if operator in ('!=', 'not in'):
            return [('id', 'not in', person_ids)]
        return [('id', 'in', person_ids)]

    workstyle_assessment_count = fields.Integer(
        string='Measurements',
        compute='_compute_workstyle_assessment_count')

    workstyle_latest_id = fields.Many2one(
        'hr.workstyle.assessment', string='Latest Measurement',
        compute='_compute_workstyle_latest')

    workstyle_d_latest = fields.Integer(
        string='D', compute='_compute_workstyle_latest', store=False,
        inverse='_inverse_workstyle_d_latest')
    workstyle_i_latest = fields.Integer(
        string='I', compute='_compute_workstyle_latest', store=False,
        inverse='_inverse_workstyle_i_latest')
    workstyle_s_latest = fields.Integer(
        string='S', compute='_compute_workstyle_latest', store=False,
        inverse='_inverse_workstyle_s_latest')
    workstyle_c_latest = fields.Integer(
        string='C', compute='_compute_workstyle_latest', store=False,
        inverse='_inverse_workstyle_c_latest')

    def _inverse_workstyle_d_latest(self):
        for employee in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.employee', employee.id, 'D', employee.workstyle_d_latest)

    def _inverse_workstyle_i_latest(self):
        for employee in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.employee', employee.id, 'I', employee.workstyle_i_latest)

    def _inverse_workstyle_s_latest(self):
        for employee in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.employee', employee.id, 'S', employee.workstyle_s_latest)

    def _inverse_workstyle_c_latest(self):
        for employee in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.employee', employee.id, 'C', employee.workstyle_c_latest)

    workstyle_gap_ids = fields.One2many(
        'hr.workstyle.gap', compute='_compute_workstyle_gap',
        string='Behavioural Gap')

    # Befattningen man JÄMFÖR mot i Beteende-fliken. Skiljer sig från
    # personens faktiska job_id: en anställd kan jämföras mot vilken roll
    # som helst (t.ex. en tänkt befordran). Default = personens egen
    # tjänst, så fliken är användbar direkt utan att man väljer något.
    match_job_id = fields.Many2one(
        'hr.job', string='Compare Against',
        default=lambda self: self.env.context.get('default_job_id'),
        help="Befattning att jämföra profilen mot. Ändra för att se hur "
             "personen matchar en annan roll.")

    # Kompetensmatchning mot den valda befattningen — VISNING som gauge.
    # Samma medvetna avsteg som behavioural_match (se
    # hr_workstyle_gap._behavioural_match): får bara visas i den enskilda
    # personens EGET formulär, aldrig i listor/kanban/sökdomäner.
    matching_score = fields.Float(
        string='Skill Match (%)', compute='_compute_matching_score',
        store=True, compute_sudo=True)
    # Därför en EGEN compute-metod: att blanda
    # lagrade och icke-lagrade fält i samma metod gör att en läsning av
    # taggarna kan skriva om gaugen (Odoo varnar för det).
    matching_skill_ids = fields.Many2many(
        'hr.skill', string='Matching Skills',
        compute='_compute_matching_skill_ids', store=False)
    missing_skill_ids = fields.Many2many(
        'hr.skill', string='Missing Skills',
        compute='_compute_matching_skill_ids', store=False)

    def _matching_skills(self):
        """Returnera (träffar, saknade) för personen mot vald befattning."""
        self.ensure_one()
        job = self.match_job_id or self.job_id
        job_skills = job.skill_ids
        return (job_skills & self.skill_ids, job_skills - self.skill_ids,
                job_skills)

    @api.depends('skill_ids', 'match_job_id', 'match_job_id.skill_ids',
                 'job_id', 'job_id.skill_ids')
    def _compute_matching_score(self):
        for employee in self:
            _matched, _missing, job_skills = employee._matching_skills()
            employee.matching_score = (
                len(_matched) / len(job_skills) * 100 if job_skills else 0)

    @api.depends('skill_ids', 'match_job_id', 'match_job_id.skill_ids',
                 'job_id', 'job_id.skill_ids')
    def _compute_matching_skill_ids(self):
        for employee in self:
            matched, missing, _job_skills = employee._matching_skills()
            employee.matching_skill_ids = matched
            employee.missing_skill_ids = missing

    # Beteendematchning mot rollens intervall — VISNING i personens egen
    # flik. Se hr_workstyle_gap._behavioural_match för varför detta är ett
    # medvetet avsteg från modulens princip, och varför fältet inte får
    # lyftas in i listor/kanban/sökdomäner.
    behavioural_match = fields.Float(
        string='Behavioural Match (%)',
        compute='_compute_behavioural_match', store=True)

    @api.depends('workstyle_latest_id', 'match_job_id',
                 'match_job_id.workstyle_line_ids',
                 'job_id', 'job_id.workstyle_line_ids')
    def _compute_behavioural_match(self):
        Gap = self.env['hr.workstyle.gap']
        for employee in self:
            # Tomt match_job_id = personens egen tjänst.
            employee.behavioural_match = Gap._behavioural_match(
                'hr.employee', employee.id,
                job=employee.match_job_id or employee.job_id)

    @api.depends('workstyle_assessment_ids')
    def _compute_workstyle_assessment_count(self):
        for employee in self:
            employee.workstyle_assessment_count = len(
                employee.workstyle_assessment_ids)

    @api.depends('workstyle_assessment_ids',
                 'workstyle_assessment_ids.date',
                 'workstyle_assessment_ids.line_ids.score')
    def _compute_workstyle_latest(self):
        for employee in self:
            latest = employee.workstyle_assessment_ids.sorted(
                key=lambda a: (a.date or fields.Date.today(), a.id),
                reverse=True)[:1]
            employee.workstyle_latest_id = latest
            scores = {}
            if latest:
                scores = {line.style_id.code: line.score
                          for line in latest.line_ids}
            employee.workstyle_d_latest = scores.get('D', 0)
            employee.workstyle_i_latest = scores.get('I', 0)
            employee.workstyle_s_latest = scores.get('S', 0)
            employee.workstyle_c_latest = scores.get('C', 0)

    @api.depends('workstyle_latest_id', 'job_id',
                 'job_id.workstyle_line_ids')
    def _compute_workstyle_gap(self):
        """Gap-rader som virtuella poster (inget skrivs till databasen).

        `Gap.new()` ger virtuella poster som försvinner när vyn stängs.
        VIKTIGT: new() tar en dict per post — inte en lista — och
        resultatet maste wrappas i browse() for att bli ett recordset
        som One2many-faltet accepterar.
        """
        Gap = self.env['hr.workstyle.gap']
        for employee in self:
            rows = Gap._rows_for('hr.employee', employee.id)
            # new() ger VIRTUELLA poster utan id — inget skrivs till
            # databasen. Det är hela poängen: gap-analysen är beräknad
            # visningsdata, aldrig lagrad sanning. (Tidigare användes
            # Gap.create(), som skrev riktiga transienta rader — det
            # motsade modellens design.)
            employee.workstyle_gap_ids = Gap.browse(
                [Gap.new(row).id for row in rows])

    def action_view_workstyle_assessments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Behavioural Measurements',
            'res_model': 'hr.workstyle.assessment',
            'view_mode': 'list,form',
            'domain': [('person_ref', '=', 'hr.employee,%s' % self.id)],
            'context': {'default_person_ref': 'hr.employee,%s' % self.id},
        }

    def action_open_workstyle_trend(self):
        """Öppna utvecklingsvyn (poäng över tid mot tjänstens zon)."""
        self.ensure_one()
        return self.env['hr.workstyle.trend'].action_open(
            'hr.employee', self.id)
