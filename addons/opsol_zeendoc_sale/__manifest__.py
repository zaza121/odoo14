# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
{
    'name': 'Zeendoc for Sale By OpenSolution',
    'version': '15.0',
    'category': 'Human resources',
    'sequence': 125,
    'description': """
Zeendoc Connector for sale By OpenSolution
=================================

This module help to send sale invoice to zeendoc

     """,
    'author': 'H.Y',
    'depends': ['opsol_zeendoc_core', 'account'],
    'data': [
        # data
        # "data/cron.xml",
        # "data/mail_message_subtype_data.xml",
        # "data/mail_template_data.xml",
        # "data/ir_sequence_data.xml",
        # security
        'security/ir.model.access.csv',
        # 'security/ir_rules.xml'
        #wizards
        'wizards/select_connector_wiz_views.xml',

        # views
        # 'views/menus.xml',
        'views/account_move_views.xml',
        'views/zeendoc_core_uploaded_file_views.xml',
        # 'views/hr_leave_type_views.xml',
        # 'views/hr_leave_views.xml',
        # 'views/pre_commande_views.xml',
        # 'views/purchase_order_views.xml',
        # 'views/budget_year_views.xml',
        # 'views/external_layout_template.xml',
        # 'views/res_company_views.xml',
        # 'views/tag_views.xml',
        # 'views/budget_department_views.xml',

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
