{
    'name': 'HR Employee views',
    'version': '12.0.0.1.1',
    'category': 'Human Resources',
    'summary': 'Hide some fields from Employee',
    'description': 'Hide some fields from Employee view',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'depends': [
        'hr', 'hr_skill', 'auth_user_rights_wizard'
    ],
    'data': [
        'views/hr_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}