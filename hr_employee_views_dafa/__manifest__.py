{
    'name': 'HR Employee views',
    'version': '12.0.0.1.3',
    'category': 'Human Resources',
    'summary': 'Hide some fields from Employee',
    'description': """Hide some fields from Employee view \n
    v12.0.0.1.2 AFC-2468 Added DAFA Admin and ServiceDesk group on SSN and Legacy ID. 
    v12.0.0.1.3 AFC-2468 added fix. 
                   """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'depends': [
        'hr', 'hr_skill', 'base_user_groups_dafa', 'hr_employee_ssn', 'hr_employee_legacy_id'
    ],
    'data': [
        'views/hr_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
