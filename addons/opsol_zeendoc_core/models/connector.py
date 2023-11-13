# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details

import logging
import json
from urllib.parse import urlparse
from collections import ChainMap
from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep.transports import Transport
import time

from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Connector(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = "opsol_zeendoc_core.connector"
    _description = "Connector Zeendoc"
    _rec_name = "name"
    # _order = "date_start desc"

    name = fields.Char(string='Name')
    address = fields.Char(string='Armoire')
    login = fields.Char(string='Login')
    password = fields.Char(string='Mou8t de passe')
    coll_id = fields.Char(string='Id Classeur')
    active = fields.Boolean(string='Active', default=True)
    index_ids = fields.One2many(
        comodel_name='opsol_zeendoc_core.connector_index',
        inverse_name='connector_id',
        string='indexes',
    )
    type_connector = fields.Selection(
        string="Type",
        selection=[("push", "Sauvegarde"), ("pull", "Importation")],
        default="push"
    )

    def test(self):
        self.ensure_one()

    @api.model
    def get_default_data(self):
        _data = {
            'Login': self.login,
            'Password': "",
            'CPassword': self.password,
            'Access_token': ""
        }
        return _data

    @api.model
    def get_fields_indexation(self, model):

        c_fields = self.index_ids.mapped("field_ids").filtered(
            lambda x: x.model == model).mapped("name")
        return c_fields

    @api.model
    def get_indexation(self, values):
        map_field = self.get_map_field_key()
        indexation = self.get_default_key_value()

        for field, value in values.items():
            indexation[map_field[field]] = value
        return indexation

    @api.model
    def get_client_zeendoc(self):
        WSDL = self.address
        user = self.login
        password = self.password

        session = Session()
        session.auth = HTTPBasicAuth(user, password)
        client = Client(WSDL, transport=Transport(session=session))

        return client

    @api.model
    def get_map_field_key(self):
        c_fieldname_zfield = self.index_ids.mapped(
            lambda x: {field.name: x.key for field in x.field_ids})
        map_field = dict(ChainMap(*c_fieldname_zfield))
        return map_field

    @api.model
    def get_default_key_value(self):
        key_defvalue = self.index_ids.filtered(
            lambda x: x.default_value).mapped(
            lambda x: {x.key: x.default_value})
        return dict(ChainMap(*key_defvalue))

    @api.model
    def get_map_key_field(self, model=None):
        c_fieldname_zfield = self.index_ids.mapped(
            lambda x: {x.key: x.field_ids.filtered(lambda x: x.model == model)})
        map_field = dict(ChainMap(*c_fieldname_zfield))
        return map_field

    def test_connexion(self):
        self.ensure_one()
        result = self.action_login()

        if result:
            raise UserError(_("Error: " + result))
        else:
            raise UserError(_("Test Ok!"))

    @api.model
    def uploadDoc(self, base64_document=None, filename=None, hash_value=None, indexation=None):
        self.ensure_one()
        self.action_login()
        _data = self.get_default_data()

        _data['Base64_Document'] = base64_document
        _data['Hash'] = hash_value
        _data['Filename'] = filename
        _data['Indexation'] = json.dumps(indexation, default=str)
        _data['Repertoire'] = ""
        _data['Id_Source'] = ""
        _data['Coll_Id'] = self.coll_id

        client = self.get_client_zeendoc()
        result = client.service.uploadDoc(**_data)
        result = json.loads(result)

        # force sychronization
        cron_task = self.sudo().env.ref(
            "opsol_zeendoc_core.cron_sync_zeendoc")
        if cron_task:
            cron_task.nextcall = fields.Datetime.now()

        return "" if result["Result"] >= 0 else result["Error_Msg"]

    @api.model
    def getAllDocument(self, filename=None, hash_value=None, indexation=None):
        self.ensure_one()

        _data = self.get_default_data()

        _data['IndexList'] = []
        _data['StrictMode'] = ""
        # _data['Fuzzy'] = ""
        _data['Order_Col'] = ""
        _data['Order'] = ""
        _data['saved_query'] = ""
        _data['saved_query_name'] = ""
        _data['Query_Operator'] = ""
        _data['From'] = ""
        _data['Nb_Results'] = ""
        _data['Get_PDF_FileSize'] = 0
        _data['Get_Original_FileSize'] = 0
        _data['Get_Comments'] = 0
        _data['Get_History'] = 0
        _data['Get_Shipment_Status'] = 0
        _data['Get_Folders_Content'] = 0
        _data['Get_Thumbs_Url'] = 0
        _data['Get_Thumbs_Size'] = 0
        _data['Value_1'] = ""
        _data['Make_Url_Independant_From_WebClient_IP'] = ""
        _data['Coll_Id'] = self.coll_id

        client = self.get_client_zeendoc()
        result = client.service.searchDoc(**_data)
        result = json.loads(result)

        if "Document" not in result.keys():
            _logger.info(_("Armoire %s:  VIDE ") % self.name)
        else:
            documents = result["Document"]
            _logger.info(_(f"Armoire {self.name}: {len(documents)} documents recuperes"))

            self.env["opsol_zeendoc_core.uploaded_file"].search(
                [("connector_id", "=", self.id)]).update(
                {"state": "delete"})
            for doc in documents:
                _doc = self.getDocument(doc["Res_Id"])
                self.create_uploadtype(_doc)

        return True

    @api.model
    def getDocument(self, res_id):
        self.ensure_one()

        _data = self.get_default_data()

        _data['Res_Id'] = res_id
        _data['Upload_Id'] = ""
        _data['Get_Comments'] = ""
        _data['Get_Lines_ConfigFile'] = ""
        _data['Make_Url_Independant_From_WebClient_IP'] = ""
        _data['Coll_Id'] = self.coll_id

        del _data["Password"]

        client = self.get_client_zeendoc()
        result = client.service.getDocument(**_data)
        result = json.loads(result)
        return result

    @api.model
    def action_login(self):
        self.ensure_one()
        _data = self.get_default_data()

        client = self.get_client_zeendoc()
        result = client.service.login(**_data)
        result = json.loads(result)
        return "" if result["Result"] >= 0 else result["Error_Msg"]

    @api.model
    def synchronize(self):
        """
            Get all the documents uploaded in Zeendoc.
        """
        connectors = self.search([])
        if not connectors:
            return False

        for connector in connectors:
            connector.getAllDocument()

    @api.model
    def create_uploadtype(self, document):
        """
            Create uploadfile from documents.
        """
        upload_obj = self.env["opsol_zeendoc_core.uploaded_file"]
        all_upload = upload_obj.search([("connector_id", "=", self.id)])

        if document["Result"] != 0:
            return False

        o = urlparse(self.address)
        prefix_url = "{}://{}". format(o.scheme, o.hostname)

        values = {}
        values["res_id"] = document["Properties"]["Res_Id"]
        values["format_document"] = document["Properties"]["Format"]
        values["download_url"] = "{}{}".format(
            prefix_url, document["Url_Original"])
        values["thumb_url"] = "{}{}".format(prefix_url, document["Url_Thumb"])
        values["date"] = document["Properties"]["Creation_Date"]
        values["filename"] = document["Properties"]["FileName"]
        values["author_name"] = document["Properties"]["Upload_User_Id_Label"]
        values["state"] = "zeendoc"
        values["connector_id"] = self.id
        values["name"] = "{}.{}".format(
            values["filename"], values["format_document"])

        elt = None
        if values["res_id"] in all_upload.mapped("res_id"):
            elt = all_upload.filtered(lambda x: x.res_id == values["res_id"])
            elt.update(values)
        else:
            elt = upload_obj.create(values)

        # handle Indexes
        indexes = document["Indexes"]
        connector_indexes = self.index_ids

        elt.update({'line_ids': [[5, 0, 0]]})  # delete all indexes

        if not indexes:
            return {}
    
        for key, value in indexes.items():
            value = ",".join(value) if type(value) == list else value
            c_index = connector_indexes.filtered(lambda x: x.key == key)
            label = c_index.label if c_index else ""
            search_field = c_index.search_field_id.id if c_index.search_field_id else None
            elt.update({
                'line_ids': [[0, 0, {'key': key, 'value': value, 'label': label, 'search_field_id': search_field}]]})


class ConnectorIndex(models.Model):
    _name = "opsol_zeendoc_core.connector_index"
    _description = "Index Connector"

    connector_id = fields.Many2one(
        comodel_name='opsol_zeendoc_core.connector',
        string='Connector',
        ondelete="cascade"
    )
    label = fields.Char(string='Label')
    key = fields.Char(string='Key')
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        relation="connector_to_field",
        string='Fields',
    )
    default_value = fields.Char(
        string='Default value',
    )
    search_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string="Champ de recherche",
    )
