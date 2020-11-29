{
    'name': 'HR User CIAM Update',
    'version': '12.0.0.1',
    'category': 'Human resources',
    'description': """This module updates user on CIAM server""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['hr', 'base', 'hr_employee_ciam_client'],
    'data': [
        'views/hr_employee_view.xml'

    ],
    'installable': True,
}
