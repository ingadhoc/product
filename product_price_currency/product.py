# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = 'product.template'

    list_price_type = fields.Selection(
        selection_add=[('other_currency', 'Other Currency')],
        )
    other_currency_id = fields.Many2one(
        'res.currency', 'Other Currency',
        help="Currency used for the Currency List Price.",
        oldname='sale_price_currency_id',
        )
    other_currency_list_price = fields.Float(
        'Sale Price on Other Currency',
        digits=dp.get_precision('Product Price'),
        help="Sale Price on Other Currency",
        oldname='sale_price_currency_id',
        )

    @api.model
    def _get_price_type(self, price_type):
        price_type = self.env['product.price.type'].search(
            [('field', '=', price_type)], limit=1)
        if not price_type:
            raise Warning(_('No Price type defined for field %s' % (
                'computed_list_price')))
        return price_type

    @api.multi
    @api.depends(
        'other_currency_list_price',
        'other_currency_id',
        )
    def _get_computed_list_price(self):
        """Only to update depends"""
        return super(product_template, self)._get_computed_list_price()

    @api.multi
    def set_prices(self):
        self.ensure_one()
        if self.list_price_type == 'other_currency':
            if not self.other_currency_id:
                raise Warning(_(
                    'You must configure "Other Currency" for product %s' % (
                        self.name)))
            _logger.info(
                'Set Prices from "computed_list_price" type "other_currency"')
            self.other_currency_list_price = self._get_price_type(
                'computed_list_price').currency_id.compute(
                self.computed_list_price, self.other_currency_id)
        else:
            return super(product_template, self).set_prices()

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'other_currency' and self.other_currency_id:
            _logger.info('Get computed_list_price for "other_currency" type')
            return self.other_currency_id.compute(
                self.other_currency_list_price, self._get_price_type(
                    'computed_list_price').currency_id)
        return super(product_template, self).get_computed_list_price()
