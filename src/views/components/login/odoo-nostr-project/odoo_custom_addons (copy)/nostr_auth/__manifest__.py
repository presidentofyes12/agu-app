# File: odoo_custom_addons/nostr_auth/__manifest__.py
{
    'name': 'Nostr Authentication',
    'version': '1.0',
    'category': 'Authentication',
    'summary': 'Extends user model with Nostr fields and authentication',
    'depends': ['base', 'auth_signup'],
    'data': [
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'external_dependencies': {
        'python': ['cryptography', 'bech32'],
    },
}
