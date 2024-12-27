{
    'name': 'Opinion Reputation with Nostr',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Opinion Reputation System with optional Nostr integration',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/opinion_reputation_views.xml',
        'data/default_questions.xml',
    ],
    'installable': True,
    'application': True,
}
