{
    'name': 'HR Department offices',
    'version': '12.0.0.2',
    'category': 'Human resources',
      "description": """
    Offices
    12.0.0.2 views
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['hr'],
    'data': [
      'views/hr_location_view.xml',
      'security/ir.model.access.csv'
    ],
    'installable': True,
}
