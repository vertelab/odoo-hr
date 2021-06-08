{
    'name': 'HR Department offices',
    'version': '12.0.0.4.1',
    'category': 'Human resources',
      "description": """
Offices
v12.0.0.2 views \n
v12.0.0.3 added group_no_one to menues to hide them from internal users \n
v12.0.0.3.1 AFC-2334: made a few fields readonly. \n
v12.0.0.4.0 AFC-2298: Fixed access rights issues. \n
v12.0.0.4.1: Fixed bug that caused recursive calls. \n
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
