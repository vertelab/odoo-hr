{
    'name': 'HR Employee Firstname Extension',
    'version': '12.0.0.1',
    'category': 'Human resources',
    'description': """
	 v12.0.0.1 AFC-666 - Hide Employee Firstname Lastname when in view-mode.
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base',
                'hr',
                'hr_employee_firstname'],
    'data': [
        'views/hr_view.xml'

    ],
    'installable': True,
}
