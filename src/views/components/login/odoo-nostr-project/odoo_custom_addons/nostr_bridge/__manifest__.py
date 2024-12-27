# File: odoo_custom_addons/nostr_bridge/__manifest__.py

{
    'name': 'Nostr Bridge',
    'version': '1.0',
    'category': 'Social',
    'summary': 'Bridge between Odoo messages, Git, and Nostr network',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'views/res_partner_views.xml',
        'views/git_repository_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['cryptography', 'gitpython', 'nostr'],
    },
}
