# -*- coding: utf-8 -*-
from datetime import datetime
import babel.dates

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    est_relever_gestion = fields.Boolean(
        string="Est un Relevé de Gestion"
    )

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        self.ensure_one()
        if product and product._name == 'product.template':
            product = product.product_variant_id
        if self.amount_type == 'code':
            company = self.env.company
            localdict = {
                'base_amount': base_amount, 'price_unit':price_unit, 'quantity': quantity,
                'product':product, 'partner':partner, 'company': company, 'tva_amount': self._context.get('tva_amount', 0)
            }
            try:
                safe_eval(self.python_compute, localdict, mode="exec", nocopy=True)
            except Exception as e:
                raise UserError(_("You entered invalid code %r in %r taxes\n\nError : %s") % (self.python_compute, self.name, e)) from e

            return localdict['result']
        return super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)

    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False, handle_price_include=True):
        taxes = self.filtered(lambda r: r.amount_type != 'code')
        company = self.env.company
        if product and product._name == 'product.template':
            product = product.product_variant_id
        for tax in self.filtered(lambda r: r.amount_type == 'code'):
            localdict = self._context.get('tax_computation_context', {})
            localdict.update({
                'price_unit': price_unit, 'quantity': quantity, 'product': product,
                'partner': partner, 'company': company, 'tva_amount': self._context.get('tva_amount', 0)
            })
            try:
                safe_eval(tax.python_applicable, localdict, mode="exec", nocopy=True)
            except Exception as e:
                raise UserError(_("You entered invalid code %r in %r taxes\n\nError : %s") % (tax.python_applicable, tax.name, e)) from e

            if localdict.get('result', False):
                taxes += tax
        return super(AccountTax, taxes).compute_all(price_unit, currency, quantity, product, partner, is_refund=is_refund, handle_price_include=handle_price_include)
