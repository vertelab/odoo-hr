# odoo-hr

Vertel HR-moduler för Odoo 18.

## Beteendeprofiler (DISC)

### `hr_workstyle` — generisk grund

Beskriver vilka **beteenden** en tjänst förväntar sig och jämför dem med en
persons nuvarande beteendeprofil. Beteende är inte kompetens: `hr_skills`
beskriver vad någon **kan**, `hr_workstyle` beskriver **hur** någon agerar.
De två taxonomierna hålls åtskilda — D/I/S/C lagras aldrig i `hr.skill`.

| Modell | Roll |
|---|---|
| `hr.workstyle.style` | Katalogen. Kod (D/I/S/C), namn, lokalt namn, färg, skala. Allt är data. |
| `hr.job.workstyle.line` | Tjänstens kravprofil: **intervall** per stil + rationale. |
| `hr.workstyle.assessment` | Mätning på `hr.employee` **eller** `hr.applicant` (polymorf). |
| `hr.workstyle.assessment.line` | Poäng per stil (1–10), med beräknad `rank`. |
| `hr.workstyle.gap` | Beräknad gap-analys (virtuella poster, inget lagras). |
| `hr.workstyle.trend` | Utveckling över tid mot tjänstens zon. |

**Intervall, inte ett tal.** En roll har ett spann av beteenden som fungerar.
Den övre gränsen är obligatorisk: utan den blir avvikelsen uppåt osynlig, och
en roll kan lida lika mycket av ett beteende som tar över som av ett som
saknas. Tre tillstånd per stil: `within` / `under_zone` / `over_zone`, plus
`unmeasured` för en kravställd stil som saknar poäng.

**Historik, inte ett fält.** Personens aktuella värden är *beräknade* från
senaste mätningen — aldrig lagrad sanning. Det gör utveckling över tid möjlig
och svarar på när och av vem ett värde sattes (samma mönster som
`hr.employee.skill.log`).

**Kopia, inte flytt, vid anställning.** När en `hr.applicant` blir anställd
kopieras mätningen till den anställde med `copied_from_id` mot originalet.
Kandidatdata kan då raderas enligt GDPR utan att den anställdes
utvecklingshistorik förstörs. Kopieringen är tyst och idempotent — fyra tal
som redan validerats av en handledare behöver ingen gransknings-wizard.

### `hr_key_behaviour` — KEY: Behaviour 5.0

Leverantörsspecifikt lager ovanpå `hr_workstyle`. Sätter färger (röd/gul/grön/
blå), terminologi, analystyper (Individ / Roll / 360° / Team), handledarens
validering, enhetsöversikt och rationale-vokabulär.

Separat modul med avsikt: färg-DISC:s ordval är specifikt för en tradition.
Låg det i grundmodulen skulle en kund med en annan leverantör få fel färger
från dag ett. Samma mönster som `hr_skill_esco` — generisk modell +
leverantörsmodul.

### DESIGNPRINCIP — beskriver beteenden, aldrig personer

Detta är inte en detalj, det är modulens gräns. Läs den innan du ändrar något
i `hr_workstyle/models/hr_workstyle_gap.py`.

**Modulen får:**
- visa zoner, staplar och avvikelser per stil
- visa utveckling över tid mot rollens zon
- säga "din I är 3, rollen förväntar 6–9 — utvecklingsområde: kommunikation"
- säga "din C är 8, rollen förväntar 2–5 — en tillgång i konsekvensanalys,
  men kan uppfattas som bromskloss i beslutstempo"
- säga "teamet har ingen med hög S — rollen som kräver förankring har ingen
  naturlig bärare"

**Modulen får aldrig:**
- producera en aggregerad matchningspoäng eller procentsats
- rangordna eller sortera personer på sin profil
- behandla `over_zone` som ett sämre resultat
- beskriva en person ("hög C = analytisk person") — bara beteendet

Skälet är dubbelt. DISC-modellens egna guardrails förbjuder att använda den
för att tilldela värde, förmåga eller potential. Och i svensk rekrytering är
ett automatiserat personlighetsbaserat urval en diskrimineringsrisk. Ett
aggregerat tal läses oundvikligen som ett betyg och blir ett
sorteringsverktyg — därför finns det inget sådant fält att sortera på.

`tests/test_hr_workstyle.py::test_no_aggregated_score_exists` bevakar detta.

### Samverkan med `cv-recruitment-bridge`

`2026-09-24-cv-competence` definierar en CV-överföring vid anställning som
**kräver granskning** (AI-parsning är osäker). Beteendemätningen kopieras
**utan** granskning. Modulerna delar därför ingen wizard och har ingen
beroendeordning — båda hakar på `create_employee_from_applicant` men oberoende
av varandra.

### Tester

```bash
sudo checkmodule -d <db> -m hr_workstyle,hr_key_behaviour -D -t -l test
```

49 tester: katalogen, kravprofilens valideringar, mätningens historik,
gap-klassificeringens symmetri, kopieringens idempotens och GDPR-beteende,
samt ett end-to-end-flöde från kandidat till utveckling över tre mätningar.

### Kända fällor (från implementationen)

- **`TransientModel` måste ha `log_access` på** i Odoo 18 (vacuum-policy).
  `_log_access = False` ger `AssertionError` vid modellbygge.
- **Inga defaults på `ideal_min`/`ideal_max`.** En default på `ideal_max`
  gör att `required=True` aldrig utlöses — kravet "utan övre gräns blir
  avvikelsen uppåt osynlig" upphör då tyst att gälla.
- **`name_get` är borttaget i Odoo 18.** Överrida `_compute_display_name`.
  Odoos egna `test_deprecation` fångar detta.
- **Computed One2many mot en `TransientModel`** måste tilldelas ett
  recordset byggt med `.new()` — inte kommandon, och `.new()` tar en dict
  per post, inte en lista.
- **`Many2oneReference` är inte `Integer`.** Ett `related`-fält mot
  `res_id` på en `Many2oneReference` ger `TypeError` vid modellbygge.
- **`hr_workstyle.gap` är virtuella poster.** Ingen tabell fylls; raderna
  försvinner när vyn stängs. `_rows_for()` skriver inget, `_build()` sparar.
