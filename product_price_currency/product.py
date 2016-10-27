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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    list_price_type = fields.Selection(
        selection_add=[('other_currency', 'Other Currency')],
    )
    other_currency_id = fields.Many2one(
        'res.currency',
        'Other Currency',
        help="Currency used for the Currency List Price.",
    )
    other_currency_list_price = fields.Float(
        'Sale Price on Other Currency',
        digits=dp.get_precision('Product Price'),
        help="Sale Price on Other Currency",
    )

    @api.multi
    @api.depends(
        'other_currency_list_price',
        'other_currency_id',
    )
    def _get_computed_list_price(self):
        """Only to update depends"""
        return super(ProductTemplate, self)._get_computed_list_price()

    @api.multi
    def set_prices(self, computed_list_price):
        self.ensure_one()
        if self.list_price_type == 'other_currency':
            if not self.other_currency_id:
                raise Warning(_(
                    'You must configure "Other Currency" for product %s' % (
                        self.name)))
            self.other_currency_list_price = self.currency_id.compute(
                computed_list_price,
                self.other_currency_id,
                round=False)
        else:
            return super(ProductTemplate, self).set_prices(
                computed_list_price)

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'other_currency':
            if self.other_currency_id:
                return self.other_currency_id.compute(
                    self.other_currency_list_price,
                    self.currency_id,
                    round=False)
            else:
                return False
        return super(ProductTemplate, self).get_computed_list_price()
