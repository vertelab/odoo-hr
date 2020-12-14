{
    'name': 'HR User CIAM Update',
    'version': '12.0.0.1',
    'category': 'Human resources',
    'description': """This module updates user on CIAM server""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['hr_employee_ciam_client', 'hr_employee_legacy_id', 'hr_employee_firstname_extension'],
    'data': [
        'views/hr_employee_view.xml'

    ],
    'installable': True,
}
