{
    'name': 'HR: Department Activity',
    'version': '0.1',
    # Version ledger: XX.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'To be able to schedule activity on department.',
    'category': 'HR',
    'description': """
        To be able to schedule activity on department.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_activity',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    'depends': ['hr'],
    'data': [
        'views/hr_department_view.xml',
    ],
    'application': False,
    'installable': True,
}
