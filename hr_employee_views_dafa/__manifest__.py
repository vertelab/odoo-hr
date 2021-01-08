{
    'name': 'HR Employee views',
    'version': '12.0.0.1.1',
    'category': 'Human Resources',
    'summary': 'Hide some fields from Employee view and added smart button to show emplyee is present or not.',
    'description': 'Hide some fields from Employee view and added smart button to show emplyee is present or not.',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'depends': [
        'hr', 'hr_holidays'
    ],
    'data': [
        'views/hr_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}