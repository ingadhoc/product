# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class product_product(models.Model):
    _inherit = "product.product"

    # lst_price now cames from computed_list_price
    lst_price = fields.Float(
        compute='_computed_get_product_lst_price',
        inverse='_computed_set_product_lst_price',
    )

    @api.multi
    @api.depends('price_extra', 'computed_list_price', 'uom_id')
    def _computed_get_product_lst_price(self):
        company_id = (
            self._context.get('company_id') or self.env.user.company_id.id)
        taxes_included = self._context.get('taxes_included')

        for product in self:
            if 'uom' in self._context:
                uom = product.uom_id
                lst_price = self.env['product.uom']._compute_price(
                    uom.id, product.computed_list_price, self._context['uom'])
            else:
                lst_price = product.computed_list_price

            # for compatibility with product_prices_taxes_included module
            if taxes_included:
                lst_price = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                    lst_price, product=product)['total_included']

            product.lst_price = lst_price + product.price_extra

    @api.multi
    def _computed_set_product_lst_price(self):
        # we dont allow taxes included and setting price for now
        if self._context.get('taxes_included'):
            raise Warning(_(
                "You can not set list price if you are working with 'Taxes "
                "Included' in the context"))

        for product in self:
            lst_price = product.lst_price
            if 'uom' in self._context:
                uom = product.uom_id
                lst_price = self.env['product.uom']._compute_price(
                    self._context['uom'], lst_price, uom.id)
            product.computed_list_price = lst_price - product.price_extra


class product_template(models.Model):
    _inherit = "product.template"

    @api.multi
    @api.depends('computed_list_price')
    def _computed_get_product_lst_price(self):
        company_id = (
            self._context.get('company_id') or self.env.user.company_id.id)
        taxes_included = self._context.get('taxes_included')

        for product in self:
            lst_price = product.computed_list_price
            if taxes_included:
                lst_price = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                    lst_price, product=product)['total_included']

            product.lst_price = lst_price

    # lst_price now cames from computed_list_price
    lst_price = fields.Float(
        compute='_computed_get_product_lst_price',
        readonly=True,
        # replace related for computed
        related=False,
    )
