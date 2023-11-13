# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details

import logging
import base64
import hashlib

from odoo import fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    upload_ref_id = fields.Many2one(
        comodel_name='opsol_zeendoc_core.uploaded_file',
        string='Zeendoc reference',
    )

    def send_to_zeendoc(self, connector_id=None):
        self.ensure_one()
        upload_obj = self.env["opsol_zeendoc_core.uploaded_file"]
        connector_obj = self.env["opsol_zeendoc_core.connector"]

        # get the onnector
        domain = [("type_connector", "=", "push")]
        if connector_id:
            domain.append(("id", "=", connector_id))
        connector = connector_obj.search(domain)
        if not connector:
            raise UserError(_("Create a zeendoc connector"))
        elif len(connector) > 1:
            action = self.sudo().env.ref(
                    'opsol_zeendoc_sale.select_connector_wiz_action').read()[0]
            action.update({'context': {
                'default_invoice_id': self.id,
                'default_connector_id': connector.ids[0]
            }})
            return action

        # prepare the data
        report_action = self.env.ref('account.account_invoices')
        attachment = report_action.sudo().retrieve_attachment(self)
        # raise Warning(attachment)
        if attachment:
            attachment.sudo().unlink()
            
        b_result, extension = report_action._render_qweb_pdf(self.ids)
        document = base64.b64encode(b_result)
        hash_code = hashlib.sha3_256()
        hash_code.update(b_result)
        _hash = hash_code.hexdigest()
        filename = "{0}.{1}".format(self.name.replace(" ", "_"), extension)
        # else:
        #     b_result = attachment.datas
        #     document = b_result
        #     hash_code = hashlib.sha3_256()
        #     hash_code.update(b_result)
        #     _hash = hash_code.hexdigest()
        #     filename = "{0}.{1}".format(self.name.replace(" ", "_"), "pdf")

        indexation_fields = connector.get_fields_indexation(self._name)
        values = self.read(indexation_fields)
        values = values[0] if values else {}
        values = {key: val for key, val in values.items() if key in indexation_fields} # filter id add by read
        values = {key: val[-1] if type(val) == tuple else val for key, val in values.items()}
        indexation = connector.get_indexation(values)

        result = connector.uploadDoc(base64_document=document, filename=filename,
                                     hash_value=_hash, indexation=indexation)
        if result:
            raise UserError(result)
        else:
            message = _("""
                La facture a ete sauvegardee dans 
                zeendoc dans l'amoire {}, veuillez patinter
                le temps la synchronisation""").format(connector.name)
            self.message_post(
                subject=_("Envoi vers Zeendoc"),
                body=message,
                message_type='comment')
