{
    'name': 'HR Department offices',
    'version': '12.0.0.3',
    'category': 'Human resources',
      "description": """
    Offices
    12.0.0.2 views \n
    12.0.0.3 added group_no_one to menues to hide them from internal users \n
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['hr'],
    'data': [
      'views/hr_location_view.xml',
      'views/hr_employee_view.xml',
      'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
}
