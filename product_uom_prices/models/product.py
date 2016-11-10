# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductSaleUom(models.Model):

    _inherit = 'product.sale.uom'

    price = fields.Float(
        'Price',
        digits=dp.get_precision('Price'),
        help="Sale Price for this UOM.",
        required=False
    )


class ProductTemplate(models.Model):

    """"""

    _inherit = 'product.template'

    list_price_type = fields.Selection(
        selection_add=[('by_uom', 'By Uom')],
    )
    uom_category_id = fields.Many2one(
        related='uom_id.category_id'
    )
    uom_price_ids = fields.One2many(
        'product.sale.uom',
        'product_tmpl_id',
        copy=True,
        string='UOM Prices',
        help="Only uoms in this list will be available in sale order lines. "
        "Set a diferent price for this uom. Set the price as 0 and the price "
        "will be calculated as sale price * uom ratio"
    )

    @api.multi
    def set_prices(self, computed_list_price):
        self.ensure_one()
        if self.list_price_type == 'by_uom':
            # self.uom_price_ids.filtered(lambda x: x.)
            # we update or create a uom line
            uom_price = self.env['product.sale.uom'].search([
                ('uom_id', '=', self.uom_id.id),
                ('product_tmpl_id', '=', self.id),
            ], limit=1)
            if uom_price:
                uom_price.price = computed_list_price
            else:
                self.env['product.sale.uom'].create({
                    'sequence': 5,
                    'uom_id': self.uom_id.id,
                    'product_tmpl_id': self.id,
                    'price': computed_list_price,
                })
        else:
            return super(ProductTemplate, self).set_prices(
                computed_list_price)

    @api.multi
    def get_uom_price(self):
        self.ensure_one()
        # If 'uom' in context we try to find a uom price
        # If not we try to return a product price for product uom
        # If not, we convert the first one to product uom
        if 'uom' in self._context:
            uom_price = self.env['product.sale.uom'].search([
                ('uom_id', '=', self._context['uom']),
                ('product_tmpl_id', '=', self.id)], limit=1)
        else:
            uom_price = self.env['product.sale.uom'].search([
                ('product_tmpl_id', '=', self.id),
                ('uom_id', '=', self.uom_id.id),
            ], limit=1)
            if not uom_price:
                uom_price = self.env['product.sale.uom'].search([
                    ('product_tmpl_id', '=', self.id)], limit=1)
        if not uom_price:
            return False
        # we convert from context uom to product uom because later
        # _price_get function convert it in the other side
        product_uom = self.uom_id
        if uom_price.uom_id != product_uom:
            return self.env['product.uom']._compute_price(
                uom_price.uom_id.id, uom_price.price, product_uom.id)
        else:
            return uom_price.price

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'by_uom':
            return self.get_uom_price()
        return super(ProductTemplate, self).get_computed_list_price()
