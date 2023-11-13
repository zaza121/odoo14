# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
from odoo import api, fields, models, _


class UploadedFile(models.Model):
    _inherit = "opsol_zeendoc_core.uploaded_file"

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string='Facture'
    )

    @api.constrains("line_ids")
    def post_update(self):

        move_obj = self.sudo().env["account.move"]
        for rec in self:
            values = rec.line_ids.mapped("value")
            result = move_obj.search([
                ("name", "in", values),
                ("upload_ref_id", "=", False)])
            for elt in result:
                elt.upload_ref_id = rec
                message = _("Document sauvegarde dans l'amoire %s Id: %d")
                elt.message_post(
                    subject=_("Envoi vers Zeendoc"),
                    body=message % (rec.connector_id.name, rec.res_id),
                    message_type='comment')
