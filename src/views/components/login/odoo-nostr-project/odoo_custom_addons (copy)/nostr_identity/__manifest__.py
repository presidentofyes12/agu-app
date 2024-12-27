# __manifest__.py
{
    'name': 'Nostr Identity Verifier',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Integrate Nostr identity verification into Odoo',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/nostr_security.xml',
        'security/ir.model.access.csv',
        'views/nostr_identity_views.xml',
        'data/ir_cron_data.xml',
    ],
    'demo': [],
    'external_dependencies': {
        'python': ['websocket-client', 'nostr'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
