# -*- coding: utf-8 -*-
"""hr.job — OKF-indexerbar (hr_ai).

VARFÖR: en jobbannons är kunskap om vad företaget söker. `description`
(Html) och `requirements` (Text) är fritext som ingen söker i idag —
de ligger i kolumner varken BM25 eller embeddings når.

Modellen äger sina KÄLLOR; `ai.okf.mixin` äger fälten och flaggan.
"""

from odoo import models, fields


class HrJob(models.Model):
    _name = 'hr.job'
    _inherit = ['hr.job', 'ai.okf.mixin']

    # OKF-taggar: egen relationstabell (en many2many kan inte ligga
    # pa en abstrakt mixin — den ger samma tabell for alla arvande).
    okf_tags = fields.Many2many(
        'ai.okf.tag', 'hr_job_okf_tag_rel', 'res_id', 'tag_id',
        string='OKF Tags')

    # ── Källor ─────────────────────────────────────────────────────────
    #
    # `okf_body`, `okf_tags` och `okf_links` är GENERISKA i mixinen:
    #   okf_body  = alla HTML/Text-fält + name
    #   okf_tags  = fält med 'tag' i namn eller målmodell
    #   okf_links = relationsfält där målet bär mixinen
    #
    # Bryggan skriver därför bara det som är specifikt för modellen.

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12)."""
        return 'hr_job'

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        Bara innehållsfält. `no_of_recruitment` och `no_of_hired_employee`
        är räknare — de ändras ofta och säger inget om texten.
        """
        return {'name', 'description', 'requirements', 'department_id',
                'industry_id', 'active'}

    def _okf_skip_reason(self):
        """Arkiverad tjänst = "tomt just nu", inte "tomt för alltid"."""
        return None

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera modellen för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är
        `@api.model` på en abstrakt modell (mätt på luke18 2026-09-22).
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('hr.job')
        return res
