{
    'name': "Telinfy Connector",
    'author': 'Rizwaan',
    'version': "17.0.0.0",
    'sequence': "0",
    'depends': ['base', 'crm', 'hr', 'odoo-rest-api', 'audio_player_widget', 'bus'],
    'data': [
        'views/crm.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}