# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Migrering 18.0.1.0.0 -> 18.0.1.1.0: res_model/res_id -> person_ref.

Bakgrund
--------
`hr.workstyle.assessment` lagrade personen som `res_model` (Selection) +
`res_id` (Many2oneReference). Det mönstret går inte att skapa från UI:t:
`res_id` är `Many2oneReference`, vars enda widget är ett rent
heltalsfält — det finns ingen persondropdown — och fältet var dessutom
`invisible="1"` i formuläret. Följden var att `res_id` alltid förblev
NULL och varje ny post kraschade på NOT NULL.

Personen lagras nu i ETT `fields.Reference`-fält, `person_ref`, med
värdet 'hr.employee,42'.

Varför pre- och inte post-migrering
-----------------------------------
`_auto_init` skapar den nya kolumnen `person_ref` som NULLABLE och lägger
på NOT NULL först i post-init-kön (`update_db_notnull` -> `post_init`).
Pre-steget körs före `_auto_init` (loading.py rad 182), så om vi lägger
till kolumnen och fyller den här hinner Odoo hitta en fylld kolumn och
sätta NOT NULL utan att `_init_column` behöver skriva något.

Kolumnen läggs till manuellt här i stället för att lita på `_auto_init`,
eftersom vi vill styra ordningen: ALTER TABLE ADD COLUMN -> UPDATE som
fyller den -> Odoo sätter NOT NULL. Om `_auto_init` hann skapa kolumnen
först vore det också ofarligt; ADD COLUMN IF NOT EXISTS är idempotent.

Kolumner som tas bort
---------------------
`res_model` och `res_id` finns inte längre som fält. Odoo tar bort deras
NOT NULL-constraint automatiskt (`_check_removed_columns`) men DROPPAR
aldrig kolumnerna själv. Vi tar bort dem explicit här — annars ligger
`res_id` kvar som NOT NULL och varje INSERT som inte rör den kraschar.
"""

import logging

from odoo.tools.sql import column_exists, table_exists

_logger = logging.getLogger(__name__)

TABLE = 'hr_workstyle_assessment'


def migrate(cr, version):
    if not version:
        # Nykodad databas — inget att migrera.
        return

    if not table_exists(cr, TABLE):
        return

    # 1. Lägg till den nya kolumnen som nullable.
    if not column_exists(cr, TABLE, 'person_ref'):
        cr.execute(
            "ALTER TABLE %s ADD COLUMN person_ref varchar" % TABLE)
        _logger.info(
            "hr_workstyle: lade till kolumnen person_ref på %s", TABLE)

    # 2. Backfyllning: 'hr.employee,42'.
    #
    #    Endast rader som faktiskt har en person kan mappas. Skulle någon
    #    rad sakna res_model/res_id fanns ingen person när posten skapades
    #    — den bryter mot modellens invariant (person_ref är required) och
    #    tas bort med en varning. Raden var ändå oanvändbar: det var
    #    precis detta tillstånd som gjorde modellen omöjlig att arbeta med.
    cr.execute("""
        UPDATE %(table)s
           SET person_ref = res_model || ',' || res_id
         WHERE person_ref IS NULL
           AND res_model IS NOT NULL
           AND res_id IS NOT NULL
    """ % {'table': TABLE})
    filled = cr.rowcount
    _logger.info("hr_workstyle: backfyllde person_ref på %s rader", filled)

    cr.execute("""
        SELECT id, res_model, res_id
          FROM %(table)s
         WHERE person_ref IS NULL
    """ % {'table': TABLE})
    orphans = cr.fetchall()
    if orphans:
        _logger.warning(
            "hr_workstyle: %s mätning(ar) saknade person (res_model/res_id "
            "NULL) och kunde inte migreras — de togs bort: %s",
            len(orphans), orphans)
        cr.execute(
            "DELETE FROM %s WHERE person_ref IS NULL" % TABLE)

    # 3. Ta bort de gamla kolumnerna. Odoo har redan släppt deras NOT NULL
    #    (_check_removed_columns), men lämnar dem kvar — och en kvarlämnad
    #    res_id är fortfarande NOT NULL och fäller varje INSERT.
    for column in ('res_model', 'res_id', 'res_name'):
        if column_exists(cr, TABLE, column):
            cr.execute("ALTER TABLE %s DROP COLUMN %s CASCADE" % (TABLE, column))
            _logger.info(
                "hr_workstyle: tog bort den föråldrade kolumnen %s.%s",
                TABLE, column)
