{
    'name': 'IVCS Git Nostr',
    'version': '1.0',
    'category': 'Version Control',
    'summary': 'Integrated Version Control System with Git and Nostr',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'depends': ['base', 'git_nostr_object', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/ivcs_item_views.xml',
        'views/res_config_settings.xml',
        'data/ir_cron_data.xml',
        'wizards/ivcs_item_wizard_views.xml',
    ],
    'external_dependencies': {
        'python': ['git', 'nostr', 'cryptography'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
