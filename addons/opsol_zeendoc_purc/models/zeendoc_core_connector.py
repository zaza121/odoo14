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
