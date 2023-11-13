# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
import logging

from odoo import api, fields, models, _


_logger = logging.getLogger(__name__)


class UploadedFile(models.Model):
    _inherit = "opsol_zeendoc_core.uploaded_file"

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string='Facture'
    )

    @api.model
    def synchronize(self):
        """
            Create vendor invoice for upload file from Zeendoc.
        """
        uploadfiles = self.search([('invoice_id', '=', False)])

        if not uploadfiles:
            return False

        for upf in uploadfiles.filtered(
                lambda x: x.connector_id.type_connector == "pull"):
            upf.create_vendor_invoice()

    def create_vendor_invoice(self):
        invoice_obj = self.env["account.move"]
        for rec in self:
            map_key_field = rec.connector_id.get_map_key_field("account.move")
            lines = self.get_map_key_value()
            values = {'move_type': 'in_invoice'}
            for key, value in lines.items():
                fields = map_key_field.get(key, [])
                for field in fields:
                    if not field.store:
                        continue
                    values[field.name] = self.convert_value(ttype=field.ttype, value=value, key=key)

            data_line = {'quantity': 1}
            if rec.connector_id.product_id:
                product = rec.connector_id.product_id
                data_line["product_id"] = product.id
                data_line["name"] = product.name
                data_line["tax_ids"] = product.supplier_taxes_id.ids
            else:
                data_line["name"] = "Article"
            data_line["price_unit"] = values["amount_untaxed"] if "amount_untaxed" in values.keys() else 0

            invoice = invoice_obj.create(values)
            invoice.update({"invoice_line_ids": [[0, 0, data_line]]})
            rec.invoice_id = invoice

    @api.constrains("line_ids")
    def post_update(self):

        move_obj = self.sudo().env["account.move"]
        for rec in self:
            values = rec.line_ids.mapped("value")
            results = move_obj.search([
                ("name", "in", values),
                ("upload_ref_id", "=", False)])

            for result in results:
                result.upload_ref_id = rec
                message = _("Document sauvegarde dans l'amoire %s Id: %d")
                result.message_post(
                    subject=_("Envoi vers Zeendoc"),
                    body=message % (rec.connector_id.name, rec.res_id),
                    message_type='comment')
