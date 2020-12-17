{
    'name': 'HR User CIAM Update',
    'version': '12.0.0.2',
    'category': 'Human resources',
    'description': """This module adds a button that runs an action that adds the user to the CIAM server""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['hr_employee_ciam_client', 'hr_employee_legacy_id', 'hr_employee_firstname_extension', 'partner_legacy_id'],
    'data': [
        'views/hr_employee_view.xml'

    ],
    'installable': True,
}
