{
    'name': 'Depreciated - HR Employee views',
    'version': '12.0.0.0',
    'category': 'Human Resources',
    'summary': 'Hide some fields from Employee view and added smart button to show emplyee is present or not.',
    'description': """
        This module has been moved to hr_employee_views_dafa
        Hide some fields from Employee view and added smart button to show emplyee is present or not.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'depends': [
        'hr', 'hr_holidays'
    ],
    'data': [
        'views/hr_views.xml',
    ],
    'installable': False,
    'auto_install': False,
}