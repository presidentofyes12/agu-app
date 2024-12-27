{
    'name': 'Decentralized Nostr Sync Manager',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Manage decentralized synchronization with Nostr and Git',
    'depends': ['base', 'ivcs_git', 'nostr_bridge'],
    'data': [
        'security/ir.model.access.csv',
        'views/sync_manager_views.xml',
        'views/dao_views.xml',
        'views/creator_views.xml',
        'views/program_views.xml',
        'views/event_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
