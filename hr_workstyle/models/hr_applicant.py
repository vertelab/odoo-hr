# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Mätningar på hr.applicant — kandidatens nuvarande beteende.

Samma mönster som hr.employee: aktuella värden härleds från senaste
mätningen. Vid anställning KOPIERAS mätningen till den anställde
(se hr_employee_hire i hr_applicant.py vidareutvecklas av
rekryteringsbryggan) — aldrig flyttas, så att GDPR-radering av
kandidatdata inte förstör den anställdes historik.
"""

from odoo import api, fields, models


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    # Compute, inte invers One2many — samma skäl och samma två fallgropar
    # som i hr_employee.py: fältet måste vara sökbart och cachen måste
    # invalideras när en mätning ändras.
    workstyle_assessment_ids = fields.One2many(
        'hr.workstyle.assessment',
        compute='_compute_workstyle_assessment_ids',
        search='_search_workstyle_assessment_ids',
        string='Behavioural Measurements')

    def _compute_workstyle_assessment_ids(self):
        Assessment = self.env['hr.workstyle.assessment']
        for applicant in self:
            applicant.workstyle_assessment_ids = Assessment.search([
                ('person_ref', '=', 'hr.applicant,%s' % applicant.id)],
                order='date desc, id desc')

    def _search_workstyle_assessment_ids(self, operator, value):
        """Översätt en domän på fältet till ett filter på hr.applicant.

        Samma skäl som i hr_employee.py: fältet är ett polymorft
        Reference och Odoo kan inte bygga en invers själv.
        """
        Assessment = self.env['hr.workstyle.assessment']

        if value is False:
            # Även här ger mapped() på ett Reference-fält en LISTA.
            found = Assessment.search(
                [('person_ref', '=like', 'hr.applicant,%')])
            ids = [a.person_ref.id for a in found if a.person_ref]
            return [('id', 'in' if operator in ('!=', 'not in') else 'not in', ids)]

        identifiers = value if isinstance(value, list) else [value]
        assessments = Assessment.search([('id', operator, identifiers)])
        # mapped() på ett Reference-fält ger en LISTA av recordsets —
        # inte ett recordset. Plocka ut id:na per post i stället.
        person_ids = [
            a.person_ref.id for a in assessments
            if a.person_ref and a.person_ref._name == 'hr.applicant']
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
        for applicant in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.applicant', applicant.id, 'D',
                applicant.workstyle_d_latest)

    def _inverse_workstyle_i_latest(self):
        for applicant in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.applicant', applicant.id, 'I',
                applicant.workstyle_i_latest)

    def _inverse_workstyle_s_latest(self):
        for applicant in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.applicant', applicant.id, 'S',
                applicant.workstyle_s_latest)

    def _inverse_workstyle_c_latest(self):
        for applicant in self:
            self.env['hr.workstyle.assessment']._set_person_score(
                'hr.applicant', applicant.id, 'C',
                applicant.workstyle_c_latest)

    workstyle_gap_ids = fields.One2many(
        'hr.workstyle.gap', compute='_compute_workstyle_gap',
        string='Behavioural Gap')

    # Befattningen man JÄMFÖR mot i Beteende-fliken. Default = personens
    # egen tjänst. Samma mönster som hr.employee.match_job_id.
    match_job_id = fields.Many2one(
        'hr.job', string='Compare Against',
        help="Befattning att jämföra profilen mot. Ändra för att se hur "
             "kandidaten matchar en annan roll.")

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
        for applicant in self:
            # Tomt match_job_id = personens egen tjänst.
            applicant.behavioural_match = Gap._behavioural_match(
                'hr.applicant', applicant.id,
                job=applicant.match_job_id or applicant.job_id)

    # ── Kompetensmatchning mot tjänsten (visning) ──────────────────────
    #
    # hr_recruitment_skills har matching_score på hr.candidate, men dess
    # compute läser context['active_id'] = TJÄNSTEN man bläddrar i. På ett
    # applicant-formulär är active_id applicantens eget id, så ett rakt
    # related-fält hade gett fel tal (oftast 0). Vi räknar därför mot den
    # VALDA befattningen (match_job_id), med personens egen tjänst som
    # fallback — rätt svar var man än öppnar posten ifrån.
    #
    # Fälten är bara VISNING (gauge + taggar). Ingen gallring, ingen
    # rangordning — samma designprincip som resten av modulen.
    matching_score = fields.Float(
        string='Skill Match (%)', compute='_compute_matching_score',
        store=True, compute_sudo=True)
    # Tagglisterna är VISNING — de lagras inte. Ett lagrat many2many
    # skulle dela tabell med skill_ids (samma relation) och krascha
    # vid registreringen. Gaugen (matching_score) är den som lagras.
    matching_skill_ids = fields.Many2many(
        'hr.skill', string='Matching Skills',
        compute='_compute_matching_skill_ids', store=False)
    missing_skill_ids = fields.Many2many(
        'hr.skill', string='Missing Skills',
        compute='_compute_matching_skill_ids', store=False)

    def _matching_skills(self):
        """Returnera (träffar, saknade, alla krav) mot vald befattning."""
        self.ensure_one()
        job = self.match_job_id or self.job_id
        job_skills = job.skill_ids
        return (job_skills & self.skill_ids, job_skills - self.skill_ids,
                job_skills)

    @api.depends('skill_ids', 'match_job_id', 'match_job_id.skill_ids',
                 'job_id', 'job_id.skill_ids')
    def _compute_matching_score(self):
        for applicant in self:
            matched, _missing, job_skills = applicant._matching_skills()
            applicant.matching_score = (
                len(matched) / len(job_skills) * 100 if job_skills else 0)

    @api.depends('skill_ids', 'match_job_id', 'match_job_id.skill_ids',
                 'job_id', 'job_id.skill_ids')
    def _compute_matching_skill_ids(self):
        for applicant in self:
            matched, missing, _job_skills = applicant._matching_skills()
            applicant.matching_skill_ids = matched
            applicant.missing_skill_ids = missing

    @api.depends('workstyle_assessment_ids')
    def _compute_workstyle_assessment_count(self):
        for applicant in self:
            applicant.workstyle_assessment_count = len(
                applicant.workstyle_assessment_ids)

    @api.depends('workstyle_assessment_ids',
                 'workstyle_assessment_ids.date',
                 'workstyle_assessment_ids.line_ids.score')
    def _compute_workstyle_latest(self):
        for applicant in self:
            latest = applicant.workstyle_assessment_ids.sorted(
                key=lambda a: (a.date or fields.Date.today(), a.id),
                reverse=True)[:1]
            applicant.workstyle_latest_id = latest
            scores = {}
            if latest:
                scores = {line.style_id.code: line.score
                          for line in latest.line_ids}
            applicant.workstyle_d_latest = scores.get('D', 0)
            applicant.workstyle_i_latest = scores.get('I', 0)
            applicant.workstyle_s_latest = scores.get('S', 0)
            applicant.workstyle_c_latest = scores.get('C', 0)

    @api.depends('workstyle_latest_id', 'job_id',
                 'job_id.workstyle_line_ids')
    def _compute_workstyle_gap(self):
        """Gap-rader som virtuella poster (inget skrivs till databasen)."""
        Gap = self.env['hr.workstyle.gap']
        for applicant in self:
            rows = Gap._rows_for('hr.applicant', applicant.id)
            applicant.workstyle_gap_ids = Gap.create(rows) if rows \
                else Gap.browse()

    def action_view_workstyle_assessments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Behavioural Measurements',
            'res_model': 'hr.workstyle.assessment',
            'view_mode': 'list,form',
            'domain': [('person_ref', '=', 'hr.applicant,%s' % self.id)],
            'context': {'default_person_ref': 'hr.applicant,%s' % self.id},
        }

    def action_open_workstyle_trend(self):
        """Öppna utvecklingsvyn (poäng över tid mot tjänstens zon)."""
        self.ensure_one()
        return self.env['hr.workstyle.trend'].action_open(
            'hr.applicant', self.id)

    # ── Överföring vid anställning ─────────────────────────────────────
    #
    # COPY, inte MOVE. Kandidatdata måste kunna raderas enligt GDPR utan
    # att den anställdes utvecklingshistorik förstörs. Därför skapas nya
    # mätningar på den anställde med `copied_from_id` mot originalet.
    #
    # Tyst kopiering — ingen gransknings-wizard. Fyra tal som redan
    # validerats av en handledare behöver ingen granskning. Det håller
    # denna modul okopplad från CV-överföringen (cv-recruitment-bridge),
    # som behöver sitt granskningssteg eftersom AI-parsning är osäker.

    def _copy_workstyle_to_employee(self, employee):
        """Kopiera kandidatens mätningar till en anställd.

        Idempotent: en mätning som redan kopierats kopieras inte igen.
        Returnerar antalet skapade mätningar.
        """
        self.ensure_one()
        Assessment = self.env['hr.workstyle.assessment']
        created = 0
        for assessment in self.workstyle_assessment_ids:
            already = Assessment.search_count([
                ('copied_from_id', '=', assessment.id),
                ('person_ref', '=', 'hr.employee,%s' % employee.id),
            ])
            if already:
                continue
            Assessment.create({
                'person_ref': 'hr.employee,%s' % employee.id,
                'date': assessment.date,
                'assessor_id': assessment.assessor_id.id,
                'source': 'recruitment',
                'note': assessment.note,
                'copied_from_id': assessment.id,
                'line_ids': [(0, 0, {
                    'style_id': line.style_id.id,
                    'score': line.score,
                }) for line in assessment.line_ids],
            })
            created += 1
        return created

    def create_employee_from_applicant(self):
        """Vidareutveckla standardflödet: kopiera beteendemätningen.

        Anropas när en kandidat blir anställd. `action['res_id']` är den
        nya anställdes id (se hr_recruitment.models.hr_candidate).
        Ingen fråga ställs — kopieringen är tyst.
        """
        action = super().create_employee_from_applicant()
        employee_id = action.get('res_id') if isinstance(action, dict) else None
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            for applicant in self:
                if applicant.workstyle_assessment_ids:
                    applicant._copy_workstyle_to_employee(employee)
        return action
