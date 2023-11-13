# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

import re

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.osv.expression import AND, expression


class PurchaseReport(models.Model):
    _name = "opsol_zeendoc_core.command_graph"
    _description = "Command Graph"
    _auto = False
    _order = 'code desc'

    id = fields.Integer(string='Id')
    command_id = fields.Integer(string='Command')
    name = fields.Char(string='Libellé de la commande')
    code = fields.Char(string='Code', default="/")
    categ_id = fields.Many2one(
        comodel_name='opsol_zeendoc_core.pre_commande_categ',
        string='Budget',
    )
    partner_text = fields.Char(string="Fournisseur")
    state = fields.Selection(
        string="Etat",
        selection=[
            ('draft', "Brouillon"),
            ("confirm", "Confirmé"),
            ("budget", "Validé par budget"),
            ("assistante", "Validé par Assist. CFO"),
            ("coordo", "Validé par Coordonateur(rice) achat"),
            ("cancel", "Annulé"),
            ("cfo", "Validé par CFO"),
            ("send", "Commande effectué"),
            ("recu", "Commande Recue"),
        ],
        default="draft"
    )
    budget_year_id = fields.Many2one(
        comodel_name='opsol_zeendoc_core.budget_year',
        string='Budget Year',
    )
    department_id = fields.Many2one(
        comodel_name="hr.department",
        string='Hr Departement',
    )
    budget_department_id = fields.Many2one(
        comodel_name="opsol_zeendoc_core.budget_department",
        string='Budget Departement',
    )
    confirm_by_id = fields.Many2one(
        comodel_name='res.users',
        string='Confirmé par',
        tracking=True
    )
    article = fields.Char(string='Article')
    quantite = fields.Float(string='Quantité')
    pu = fields.Float(string='Prix unitaire')
    total = fields.Float(string='Sous total')
    bud_state = fields.Selection(
        string="Budget Year state",
        selection=[
            ('draft', 'Draft'),
            ('open', "Open"),
            ('close', 'Closed'),
            ('cancel', 'Cancel')],
        default="draft"
    )
    date_command = fields.Date(string="Date Order")

    @property
    def _table_query(self):
        ''' . '''
        return '%s %s %s' % (self._select(), self._from(), self._group_by())

    def _select(self):
        select_str = """
            SELECT
                pco.id as command_id,
                min(l.id) as id,
                -- po.date_order as date_order,
                pco.state,
                bud.state as bud_state,
                -- po.date_approve,
                pco.name,
                pco.code,
                pco.categ_id,
                pco.partner_text,
                pco.budget_year_id,
                pco.department_id,
                pco.budget_department_id,
                pco.confirm_by_id,
                pco.date_command,
                l.article,
                l.quantite,
                l.pu,
                l.total
        """
        return select_str

    def _from(self):
        from_str = """
            FROM opsol_zeendoc_core_pre_commande_line l
                join opsol_zeendoc_core_pre_commande pco on (l.command_id=pco.id)
                left join opsol_zeendoc_core_budget_year bud on (pco.budget_year_id=budget_year_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
               pco.id, l.article,l.quantite,l.pu, l.total, bud_state
        """
        return group_by_str
