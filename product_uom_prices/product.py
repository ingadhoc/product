# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, _, api
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class product_uom_price(models.Model):

    """"""

    _name = 'product.uom.price'
    _description = 'Product Uom Price'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template'
        )
    uom_id = fields.Many2one(
        'product.uom',
        string='UOM',
        required=True,
        )
    price = fields.Float(
        'Price',
        digits=dp.get_precision('Price'),
        help="Sale Price for this UOM.",
        required=True
        )

    _sql_constraints = [
        ('price_uniq', 'unique(product_tmpl_id, uom_id)',
            'UOM mast be unique per Product Template!'),
    ]


class product_template(models.Model):

    """"""

    _inherit = 'product.template'

    list_price_type = fields.Selection(
        selection_add=[('by_uom', 'By Uom')],
        )
    uom_category_id = fields.Many2one(
        related='uom_id.category_id'
        )
    uom_price_ids = fields.One2many(
        'product.uom.price',
        'product_tmpl_id',
        string='UOM Prices',
        help="Only uoms in this list will be available in sale order lines. "
        "Set a diferent price for this uom. Set the price as 0 and the price "
        "will be calculated as sale price * uom ratio")

    @api.one
    @api.constrains('uom_price_ids')
    def _check_uoms(self):
        uom_categ_ids = [x.uom_id.category_id.id for x in self.uom_price_ids]
        uom_categ_ids = list(set(uom_categ_ids))
        uom_ids = [x.uom_id.id for x in self.uom_price_ids]
        if self.uom_id.id in uom_ids:
            raise Warning(_('UOM %s is the default product uom, \
                you can not se it in UOM prices') % (self.uom_id.name))
        if (
                len(uom_categ_ids) > 1 or
                (uom_categ_ids and
                    uom_categ_ids[0] != self.uom_id.category_id.id)
                ):
            raise Warning(_('UOM Prices Category must be of the same \
                UOM Category as Product Unit of Measure'))

    @api.multi
    def set_prices(self):
        self.ensure_one()
        if self.list_price_type == 'by_uom':
            _logger.info(
                'Set Prices from "computed_list_price" type "by_uom"')
            self.list_price = self.computed_list_price
        else:
            return super(product_template, self).set_prices()

    @api.multi
    def get_uom_price(self):
        self.ensure_one()
        """
        If 'uom' in context we try to find a uom prices
        If we don't found or 'uom' not in context, we return false
        """
        uom_prices = False
        if 'uom' in self._context:
            uom_prices = self.env['product.uom.price'].search([
                        ('uom_id', '=', self._context['uom']),
                        ('product_tmpl_id', '=', self.id)])
        if uom_prices:
            product_uom = self.uom_id or self.uos_id
            # we convert from context uom to product uom because later
            # _price_get function convert it in the other side
            return self.env['product.uom']._compute_price(
                self._context['uom'], uom_prices.price, product_uom.id)
        else:
            return False

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'by_uom':
            _logger.info('Get computed_list_price for "by_uom" type')
            return self.get_uom_price() or self.list_price
        return super(product_template, self).get_computed_list_price()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
