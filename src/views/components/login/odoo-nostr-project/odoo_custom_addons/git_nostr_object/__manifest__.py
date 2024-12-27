{
    'name': 'git_nostr_object',
    'version': '1.0',
    'depends': ['base', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/git_repository_views.xml',
        'views/git_commit_views.xml',
        'views/git_tree_views.xml',
        'views/git_blob_views.xml',
        'views/git_object_views.xml',
        'views/nostr_event_object_views.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/admin_test_views.xml',
        'views/git_commit_wizard_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'git_nostr_object/static/src/js/git_nostr_notifications.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
