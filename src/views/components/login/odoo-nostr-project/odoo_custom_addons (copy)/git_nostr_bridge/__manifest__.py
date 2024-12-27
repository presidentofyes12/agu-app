{
    'name': 'Git-Nostr Bridge',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Integrates Git repositories with Nostr network',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'depends': ['base', 'mail', 'nostr_auth', 'nostr_bridge', 'integrated_ivcs'],
    'data': [
        'security/ir.model.access.csv',
        'views/git_repository_views.xml',
        'views/nostr_event_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'wizard/create_nostr_event_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['git', 'nostr', 'websockets'],
    },
}
