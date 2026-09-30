# -*- coding: utf-8 -*-
{
    'name': 'HR: AI',
    'version': '18.0.1.0.0',
    'summary': 'OKF-indexering av hr.job och hr.employee',
    'category': 'Hidden',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Bryggmodul för OKF-indexering av HR-modellerna.

        Lägger `ai.okf.mixin` på hr.job och hr.employee så att de blir
        OKF-koncept.

        VARFÖR DESSA: en jobbannons är kunskap om vad företaget söker,
        och en medarbetares roll är kunskap om vem som kan vad. Båda
        ligger i fritextfält som varken BM25 eller embeddings ser idag.

        INTEGRITET: hr.employee bär personuppgifter i gruppbegränsade
        fält (ssnid, private_email, private_phone, spouse_*, place_of_birth).
        Mixinens källor hoppar över ALLA fält med `groups=` — de kopieras
        aldrig till ett koncept. Se ai_agent_core/models/ai_okf_mixin.py.

        Modellerna äger sina KÄLLOR; mixinen i ai_agent_core äger fälten
        och flaggan. Ingen domän nämns i kärnan.
    """,
    'depends': [
        'ai_agent_core',
        'hr',
    ],
    'data': [
        'data/okf_artifact_types_hr.xml',
        'data/okf_debug_actions.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
