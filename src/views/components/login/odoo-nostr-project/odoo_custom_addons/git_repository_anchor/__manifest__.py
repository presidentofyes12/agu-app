{
    'name': 'Git Repository Anchor',
    'version': '1.0',
    'category': 'Development',
    'summary': 'Manage Git repositories using Nostr events',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/git_repository_security.xml',
        'security/ir.model.access.csv',
        'views/git_repository_views.xml',
        'views/nostr_event_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['git', 'nostr'],
    },
}
