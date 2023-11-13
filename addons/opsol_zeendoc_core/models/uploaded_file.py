# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details

import logging
import base64
import hashlib
import requests
from datetime import datetime
from collections import ChainMap

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class UploadedFile(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = "opsol_zeendoc_core.uploaded_file"
    _description = "Uploaded File"

    name = fields.Char(string='Name')
    res_id = fields.Integer(string='Ressource Id')
    format_document = fields.Char(string='Format')
    file = fields.Binary(
        string='Apercu Document',
        compute='_compute_file', store=True,
        attachment=True
    )
    thumb_url = fields.Char(string='Url apercu')
    download_url = fields.Char(string='Url Download')
    date = fields.Datetime(
        string='Date envoi', required=True, tracking=True,
        default=fields.Datetime.now())
    filename = fields.Char(string='Filename')
    hash_value = fields.Char(string='Hash')
    author_name = fields.Char(string='Cree par')
    state = fields.Selection(
        [('draft', 'Brouillon'), ('zeendoc', 'Zeendoc'), ('delete', 'Supprime')],
        string="state",
        default="draft"
    )
    connector_id = fields.Many2one(
        comodel_name='opsol_zeendoc_core.connector',
        string='connector',
    )
    line_ids = fields.One2many(
        comodel_name='opsol_zeendoc_core.uploaded_file_line',
        inverse_name='uploadfile_id',
        string='Lines'
    )

    @api.model
    def load_image_from_url(self, url):
        data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        return data

    @api.model
    def convert_value(self, ttype="", value=None, key=None):
        if ttype == "date":
            return datetime.strptime(value, "%d/%m/%Y")
        elif ttype == "datetime":
            return datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
        elif ttype == "many2one":
            line = self.line_ids.filtered(lambda x: x.key == key)

            if line and line.search_field_id:

                if line.search_field_id.ttype in ["integer", "many2one"]:
                    try:
                        identifiant = int(value)
                        result = self.sudo().env[line.search_field_id.model].search(
                            [(line.search_field_id.name, "=", identifiant)], limit=1)
                        if result:
                            return result.id
                    except:
                        return None
                else:
                    try:
                        domain = [(line.search_field_id.name, "ilike", value)]
                        result = self.sudo().env[line.search_field_id.model].search(
                            domain, limit=1)
                        if result:
                            return result.id
                    except:
                        return None
                return None
            else:
                try:
                    return int(value)
                except:
                    return None
        else:
            return value

    @api.model
    def get_map_key_value(self):
        lines = self.line_ids.mapped(lambda x: {x.key: x.value})
        return dict(ChainMap(*lines))

    @api.depends('thumb_url')
    def _compute_file(self):
        for record in self:
            image = None
            if record.thumb_url:
                image = self.load_image_from_url(record.thumb_url)
            record.update({'file': image, })


class UploadedFileIndex(models.Model):
    _name = "opsol_zeendoc_core.uploaded_file_line"
    _description = "Uploaded File Index"

    uploadfile_id = fields.Many2one(
        comodel_name='opsol_zeendoc_core.uploaded_file',
        string='Fichier',
        ondelete="cascade"
    )

    key = fields.Char(string='Key')
    label = fields.Char(string='Label')
    value = fields.Char(string='Value')
    search_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string="Champ de recherche",
    )
