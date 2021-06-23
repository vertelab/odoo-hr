{
    "name": "HR Outplacement Tab",
    "version": "12.0.0.0",
    "author": "Vertel AB",
    "description": """
        This module adds a tab with "Assigned outplacements" on the "HR-employee"-form.\n
    """,
    "license": "AGPL-3",
    "website": "https://vertel.se/",
    "depends": [
        'sale', 'hr', 'outplacement'
    ],
    "category": "HR",
    "data": [
        'views/hr_views.xml',
    ],
    "application": False,
    "installable": True,
}
