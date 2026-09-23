# -*- coding: utf-8 -*-
"""hr.employee — OKF-indexerbar (hr_ai).

VARFÖR: en medarbetares roll är kunskap om vem som kan vad. `job_title`
och `notes` beskriver det.

INTEGRITET — DETTA ÄR MODULENS VIKTIGASTE RAD:

hr.employee bär personuppgifter i gruppbegränsade fält:
    ssnid              personnummer
    private_email      privat e-post
    private_phone      privat telefon
    private_street     privat adress
    spouse_complete_name, spouse_birthdate
    place_of_birth, birthday

Mixinen hoppar över ALLA fält med `groups=` (ai_okf_mixin.py). Det är
inte en detalj: ett koncept är sökbart för alla som får läsa koncept,
och att kopiera personnummer dit vore en GDPR-incident. Källorna
filtrerar därför på `field.groups` — inte på en lista i den här filen,
som skulle glömmas när Odoo lägger till ett fält.

Modellen äger sina KÄLLOR; `ai.okf.mixin` äger fälten och flaggan.
"""

from odoo import models, fields


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'ai.okf.mixin']

    # OKF-taggar: egen relationstabell (en many2many kan inte ligga
    # pa en abstrakt mixin — den ger samma tabell for alla arvande).
    okf_tags = fields.Many2many(
        'ai.okf.tag', 'hr_employee_okf_tag_rel', 'res_id', 'tag_id',
        string='OKF Tags')

    # ── Källor ─────────────────────────────────────────────────────────
    #
    # `okf_tags` och `okf_links` är generiska.
    # `okf_body` överrids: se nedan.

    def _okf_body_source(self):
        """Medarbetarens roll och ansvar.

        VARFÖR ÖVERRIDNING: den generiska källan tar HTML/Text + `name`.
        För hr.employee är `notes` (det enda Text-fältet) gruppbegränsat
        och hoppas därför över — kvar blir bara `name`, och kroppen blir
        tom för en användare utan hr.group_hr_user (mätt 2026-09-23).

        Vi lägger därför till `job_title` (Char): den är också
        gruppbegränsad, men den beskriver ROLLEN, inte personen. Att
        indexera "Drifttekniker" är inte en integritetsfråga.

        MEDVETET UTELÄMNADE: ssnid, private_email, private_phone,
        private_street, private_city, private_zip, spouse_*,
        place_of_birth, birthday. Personuppgifter hör inte i ett koncept.
        """
        self.ensure_one()
        parts = []
        for value in (self.name, self.job_title):
            if value:
                parts.append(str(value).strip())
        # `notes` är gruppbegränsat — bara om användaren faktiskt får
        # läsa det. `_okf_field_readable()` kontrollerar behörigheten
        # uttryckligen i stället för att lita på att värdet råkade vara
        # tomt (Odoo filtrerar vid läsning, men det är ett svagare skydd).
        if self.notes and self._okf_field_readable('notes'):
            parts.append(str(self.notes).strip())
        return '\n\n'.join(p for p in parts if p)

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12)."""
        return 'hr_employee'

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        MEDVETET UTAN personuppgifter: `ssnid`, `private_*` och
        `spouse_*` får inte ens flagga en omindexering — de läses
        aldrig av källorna (gruppbegränsade).
        """
        return {'name', 'job_title', 'job_id', 'department_id',
                'notes', 'active'}

    def _okf_skip_reason(self):
        """Arkiverad medarbetare = "tomt just nu", inte "tomt för alltid"."""
        return None

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera modellen för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är
        `@api.model` på en abstrakt modell (mätt på luke18 2026-09-22).
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('hr.employee')
        return res
