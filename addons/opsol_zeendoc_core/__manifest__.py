# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
{
    'name': 'Zeendoc By OpenSolution',
    'version': '15.0',
    'category': 'Human resources',
    'sequence': 125,
    'description': """
Zeendoc Connector By OpenSolution
=================================

This module help to create a connector to communicate with Zeendoc

     """,
    'author': 'H.Y',
    'depends': ['web','base', 'mail'],
    'data': [
        # data
        "data/cron.xml",
        # security
        'security/ir.model.access.csv',

        # views
        'views/menus.xml',
        'views/connector_views.xml',
        'views/uploaded_file_views.xml',

        # reports
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
    "external_dependencies": {"python": ["zeep"]},
    'assets': {
        'web.assets_qweb': [
            'opsol_zeendoc_core/static/src/xml/*.xml',
        ],
    },
}
