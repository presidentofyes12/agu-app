{
    'name': 'Nostr Publisher',
    'version': '1.5',
    'category': 'Social Network',
    'summary': 'Publish and manage events on the Nostr network',
    'sequence': 10,
    'description': """
    This module allows publishing events to the Nostr network and manages Nostr publishers, relays, and connected modules.
    It also serves as a communication layer for other Odoo modules.
    
    Features:
    - Create and manage Nostr publishers
    - Configure and monitor Nostr relays
    - Track connected modules using Nostr for communication
    - Publish events to the Nostr network
    - View publishing statistics and logs
    - Act as a communication layer for inter-module messaging
    - Submit Nostr events through a user-friendly wizard
    - Integration with GitLab-Nostr Bridge for enhanced functionality
    - Automatic connection to GitLab-Nostr Bridge as a connected module
    - Test and manage relay connections
    - Automatically update active relays
    """,
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'depends': ['base', 'mail', 'queue_job', 'gitlab_nostr_bridge'],
    'data': [
        'security/nostr_security.xml',
        'security/ir.model.access.csv',
        'views/nostr_publisher_views.xml',
        'views/menu_items.xml',
        'wizards/submit_event_wizard_view.xml',
        'data/ir_cron.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['websockets', 'secp256k1'],
    },
    'assets': {
        'web.assets_backend': [
            'nostr_publisher/static/src/js/json_tags_widget.js',
            'nostr_publisher/static/src/xml/json_tags_widget.xml',
            'nostr_publisher/static/src/js/nostr_publisher.js',
            'nostr_publisher/static/src/xml/nostr_publisher.xml',
        ],
    },
    'license': 'LGPL-3',
}
