# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "HR Tier Validation",
    "summary": """
        HR Tier Validation
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://vertel.se/apps/odoo-hr/hr_tier_validation",
    "depends": ['hr', 'project_purchase','base_tier_validation'],
    "data": [
        'views/hr_department_views.xml',
        'views/tier_definition_views.xml',
    ],
}
