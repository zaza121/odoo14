# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
{
    'name': 'Zeendoc for Purchase By OpenSolution',
    'version': '15.0',
    'category': 'Human resources',
    'sequence': 125,
    'description': """
Zeendoc Connector for purchase By OpenSolution
=================================

This module help to save purchase invoice to zeendoc

     """,
    'author': 'H.Y',
    'depends': ['opsol_zeendoc_core', 'account'],
    'data': [
        # data
        "data/cron.xml",
        # security
        'security/ir.model.access.csv',
        # 'security/ir_rules.xml'
        #wizards
        'wizards/select_connector_wiz_views.xml',

        # views
        'views/account_move_views.xml',
        'views/zeendoc_core_uploaded_file_views.xml',
        'views/zeendoc_core_connector_views.xml',

        # reports
        # 'reports/paper_format.xml',
        # 'reports/pre_commande_report.xml',
        # 'reports/command_graph_views.xml',
        # 'reports/rapport_conge_graph_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_qweb': [
            'opsol_zeendoc_core/static/src/xml/*.xml',
        ],
    },
}
