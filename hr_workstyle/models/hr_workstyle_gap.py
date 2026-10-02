# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Gap-analys: tjänstens förväntade beteende mot personens nuvarande.

DESIGNPRINCIP — läs denna innan du ändrar något här.

Modulen beskriver beteenden, aldrig personer. Därför:

  * INGEN aggregerad matchningspoäng. Ingen procentsats. Ingen summa.
    Ett sådant tal läses oundvikligen som ett betyg och blir ett
    sorteringsverktyg.
  * INGEN rangordning av personer.
  * `over_zone` är INTE ett sämre resultat. Det är en avvikelse från
    rollens förväntan — en VD med maximalt C kan lida av
    analysförlamning, men personen är inte sämre för det.

DISC-modellens egna guardrails förbjuder att använda den för att tilldela
värde, förmåga eller potential. I svensk rekrytering är ett automatiserat
personlighetsbaserat urval dessutom en diskrimineringsrisk.

Modellen är en TransientModel: raderna är beräknade visningsdata som
byggs per läsning och städas av Odoos autovacuum. Ingen sanning lagras
här — sanningen är mätningen (hr.workstyle.assessment) och kravet
(hr.job.workstyle.line).

Fyra tillstånd per stil: within / under_zone / over_zone, plus unmeasured
för en kravställd stil som saknar poäng.
"""

from odoo import api, fields, models


class HrWorkstyleGap(models.TransientModel):
    _name = 'hr.workstyle.gap'
    _description = 'Behavioural Gap (requirement vs measurement)'
    _order = 'style_sequence, style_id'

    # TransientModel MÅSTE ha log_access på i Odoo 18 (vacuum-policy).
    # Sätt det därför inte till False.

    # Kopplingen till personen är en lös referens (inte en inverse):
    # raderna skapas av personen och städas av autovacuum. Det gör att
    # gap-vyn kan läsas från hr.employee och hr.applicant utan att en
    # computed One2many mot en TransientModel behöver tilldelas.
    res_model = fields.Selection([
        ('hr.employee', 'Employee'),
        ('hr.applicant', 'Applicant'),
    ], string='Applies To', index=True)
    res_id = fields.Integer(string='Record')
    job_id = fields.Many2one('hr.job', string='Job Position')
    style_id = fields.Many2one('hr.workstyle.style', string='Behavioural Style')
    style_sequence = fields.Integer(
        related='style_id.sequence', string='Sequence')
    style_code = fields.Char(related='style_id.code', string='Code')

    ideal_min = fields.Integer(string='From')
    ideal_max = fields.Integer(string='To')
    value = fields.Integer(string='Current')

    deviation = fields.Selection([
        ('within', 'Within range'),
        ('under_zone', 'Below range'),
        ('over_zone', 'Above range'),
        ('unmeasured', 'Not measured'),
    ], string='Deviation')

    importance = fields.Selection([
        ('nice_to_have', 'Nice to have'),
        ('important', 'Important'),
        ('critical', 'Critical'),
    ], string='Importance')

    rationale = fields.Text(string='Rationale')

    @api.model
    def _classify(self, value, ideal_min, ideal_max):
        """Klassificera ett värde mot ett intervall.

        Symmetrisk: både under och över är avvikelse. Ett saknat värde
        är omätt, aldrig noll.
        """
        if not value:
            return 'unmeasured'
        if value < ideal_min:
            return 'under_zone'
        if value > ideal_max:
            return 'over_zone'
        return 'within'

    @api.model
    def _rows_for(self, res_model, res_id):
        """Gap-rader för en person mot personens tjänst.

        Returnerar en lista av dicts. Tom lista när personen saknar
        tjänst, när tjänsten saknar kravprofil, eller när personen inte
        finns — ingen gap-analys produceras då.
        """
        record = self.env[res_model].browse(res_id).exists()
        if not record:
            return []

        job = record.job_id
        if not job or not job.workstyle_line_ids:
            return []

        latest = record.workstyle_latest_id
        scores = {}
        if latest:
            scores = {line.style_id.id: line.score for line in latest.line_ids}

        result = []
        for line in job.workstyle_line_ids:
            value = scores.get(line.style_id.id, 0)
            result.append({
                'res_model': res_model,
                'res_id': res_id,
                'job_id': job.id,
                'style_id': line.style_id.id,
                'ideal_min': line.ideal_min,
                'ideal_max': line.ideal_max,
                'value': value,
                'deviation': self._classify(
                    value, line.ideal_min, line.ideal_max),
                'importance': line.importance,
                'rationale': line.rationale,
            })
        return result

    @api.model
    def _build(self, res_model, res_id):
        """Bygg och spara gap-rader för en person.

        Används av personens form-vy (en knapp eller en server action)
        när raderna behöver vara klickbara poster. För ren visning är
        `_rows_for` att föredra — den skriver inget.
        """
        self.search([('res_model', '=', res_model),
                     ('res_id', '=', res_id)]).unlink()
        rows = self._rows_for(res_model, res_id)
        return self.create(rows) if rows else self.browse()
