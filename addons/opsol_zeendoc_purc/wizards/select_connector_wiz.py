# -*- coding: utf-8 -*-

import datetime
from odoo import _, api, fields, models


class SelectConnectorWiz(models.TransientModel):
    _name = 'wizard.opsol_zeendoc_sale.select_connector'
    _description = 'Select connector Invoice'

    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Facture',
    )
    connector_id = fields.Many2one(
        comodel_name='opsol_zeendoc_core.connector',
        string='Armoire',
    )

    def do_ation(self):
        self.ensure_one()
        return self.invoice_id.send_to_zeendoc(
            connector_id=self.connector_id.id)
