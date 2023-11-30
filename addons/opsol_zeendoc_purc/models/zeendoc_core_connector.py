# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
from odoo import api, fields, models, _


class CoreConnector(models.Model):
    _inherit = "opsol_zeendoc_core.connector"

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Produit pour achat',
    )
    auto_create_bill = fields.Boolean(
        string='Auto create vendor bill',
        default=False
    )

    @api.model
    def prepare_index_lines_with_values(self, indexes):
        connector_indexes = self.index_ids
        result = []
        for key, value in indexes.items():
            value = ",".join(value) if type(value) == list else value
            c_index = connector_indexes.filtered(lambda x: x.key == key)
            label = c_index.label if c_index else ""
            search_field = c_index.search_field_id.id if c_index.search_field_id else None
            is_expense_account = c_index.is_expense_account
            result.append([0, 0, {'key': key, 'value': value, 'label': label, 'search_field_id': search_field, 'is_expense_account': is_expense_account}])
        return result


class ConnectorIndex(models.Model):
    _inherit = "opsol_zeendoc_core.connector_index"

    is_expense_account = fields.Boolean(string='Est un compte comptable', default=False)    
