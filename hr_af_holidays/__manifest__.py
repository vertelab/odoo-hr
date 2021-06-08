{
    'name':     'AF Public Holidays',
    'summary':  'A list of public holidays and shortened work days at AF.',
    'version':  '12.0.1.0.0',
    'category': 'Human Resources',
    'sequence': '10',
    'license':  'AGPL-3',
    'author':   'Arbetsförmedlingen',
    'website':  'https://arbetsformedlingen.se/',
    'depends':  [
        'resource', 
    ],
    'data': [
        'data/resource.calendar.leaves.csv',
 
    ],
    'installable': True,
    'application': True,
}