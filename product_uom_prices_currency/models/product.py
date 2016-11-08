# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import UserError
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

    @api.one
    @api.depends('price', 'product_tmpl_id.other_currency_id')
    def get_price_on_base_currency(self):
        template = self.product_tmpl_id
        if template.other_currency_id and self.price:
            self.price_on_base_currency = template.other_currency_id.compute(
                self.price,
                template.currency_id,
                round=False)


class ProductTemplate(models.Model):

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
        if self.list_price_type == 'by_uom_currency' and computed_list_price:
            if not self.other_currency_id:
                raise UserError(_(
                    'You must configure "Other Currency" for product %s' % (
                        self.name)))
            uom_price = self.env['product.sale.uom'].search([
                ('uom_id', '=', self.uom_id.id),
                ('product_tmpl_id', '=', self.id),
            ], limit=1)
            other_currency_price = (
                self.currency_id.compute(
                    computed_list_price, self.other_currency_id, round=False))
            if uom_price:
                uom_price.price = other_currency_price
            else:
                self.env['product.sale.uom'].create({
                    'sequence': 5,
                    'uom_id': self.uom_id.id,
                    'product_tmpl_id': self.id,
                    'price': other_currency_price,
                })
        else:
            return super(ProductTemplate, self).set_prices(
                computed_list_price)

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'by_uom_currency':
            price = self.get_uom_price()
            if self.other_currency_id and price:
                return self.other_currency_id.compute(
                    price,
                    self.currency_id,
                    round=False)
            else:
                return False
        return super(ProductTemplate, self).get_computed_list_price()
