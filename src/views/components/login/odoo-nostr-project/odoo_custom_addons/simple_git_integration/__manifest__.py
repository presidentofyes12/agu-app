{
    'name': 'Simple Git Integration',
    'version': '1.0',
    'category': 'Development',
    'summary': 'Simple Git integration for managing code repositories.',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/git_repository_views.xml',
        'views/git_commit_views.xml',
        'wizards/create_commit_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
