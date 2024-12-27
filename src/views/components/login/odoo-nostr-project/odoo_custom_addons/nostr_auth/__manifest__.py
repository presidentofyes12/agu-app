{
    'name': 'Nostr Authentication',
    'version': '1.0',
    'category': 'Authentication',
    'summary': 'Extends user model with Nostr fields and authentication',
    'depends': ['base', 'auth_signup', 'web'],  # Added web dependency
    'data': [
        'security/nostr_security.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'external_dependencies': {
        'python': ['cryptography', 'bech32', 'websockets', 'nostr'],
    },
}
