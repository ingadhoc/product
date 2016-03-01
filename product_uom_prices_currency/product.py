# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, _, api
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductSaleUom(models.Model):

    """"""

    _inherit = 'product.sale.uom'

    price_on_base_currency = fields.Float(
        'Price',
        digits=dp.get_precision('Product Price'),
        compute='get_price_on_base_currency'
        )
    price = fields.Float(
        string='Price on Other Currency',
        help='This will be the stored price',
        )

    @api.one
    @api.depends('price', 'product_tmpl_id.other_currency_id')
    def get_price_on_base_currency(self):
        template = self.product_tmpl_id
        if template.other_currency_id:
            self.price_on_base_currency = template.other_currency_id.compute(
                self.price,
                template.computed_list_price_currency_id,
                round=False)
        else:
            self.price_on_base_currency


class product_template(models.Model):

    """"""

    _inherit = 'product.template'

    list_price_type = fields.Selection(
        selection_add=[('by_uom_currency', 'By UOM and Currency')],
        )
    other_currency_uom_price_ids = fields.One2many(
        # related='uom_price_ids'
        # we dont use related becuase with onchange it changes this field
        # and try to create two times the same record
        'product.sale.uom',
        'product_tmpl_id',
        string='UOM Prices',
        copy=True,
        help="Only uoms in this list will be available in sale order lines. "
        "Set a diferent price for this uom. Set the price as 0 and the price "
        "will be calculated as sale price * uom ratio"
        )

    @api.multi
    def set_prices(self, computed_list_price):
        self.ensure_one()
        if self.list_price_type == 'by_uom_currency':
            if not self.other_currency_id:
                raise Warning(_(
                    'You must configure "Other Currency" for product %s' % (
                        self.name)))
            self.other_currency_list_price = self._get_price_type(
                'computed_list_price').currency_id.compute(
                computed_list_price, self.other_currency_id, round=False)
        else:
            return super(product_template, self).set_prices(
                computed_list_price)

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'by_uom_currency':
            uom_price = self.get_uom_price()
            if self.other_currency_id and uom_price:
                return self.other_currency_id.compute(
                    uom_price,
                    self._get_price_type('computed_list_price').currency_id,
                    round=False)
            else:
                return False
        return super(product_template, self).get_computed_list_price()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
