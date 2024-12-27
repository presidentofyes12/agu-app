{
    'name': 'Atom System',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'A flexible, atom-based data management system',
    'sequence': 10,
    'license': 'LGPL-3',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/atom_security.xml',
        'security/ir.model.access.csv',
        'views/atom_views.xml',
        'views/atom_menus.xml',
        'views/atom_templates.xml',
        'data/atom_data.xml',
    ],
    'demo': [
        'data/atom_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'atom_system/static/src/js/**/*',
            'atom_system/static/src/css/**/*',
        ],
    },
}