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
    @api.depends('price_extra', 'computed_list_price', 'uom_id', 'uos_id')
    def _computed_get_product_lst_price(self):
        for product in self:
            if 'uom' in self._context:
                uom = product.uos_id or product.uom_id
                lst_price = self.env['product.uom']._compute_price(
                    uom.id, product.computed_list_price, self._context['uom'])
            else:
                lst_price = product.computed_list_price
            product.lst_price = lst_price + product.price_extra

    @api.multi
    def _computed_set_product_lst_price(self):
        # for compatibility with product_prices_taxes_included module
        if self._context.get('taxes_included'):
            raise Warning(_(
                "You can not set list price if you are working with 'Taxes "
                "Included' in the context"))

        for product in self:
            lst_price = product.lst_price
            if 'uom' in self._context:
                uom = product.uos_id or product.uom_id
                lst_price = self.env['product.uom']._compute_price(
                    self._context['uom'], lst_price, uom.id)
            product.computed_list_price = lst_price - product.price_extra

    def price_get(
            self, cr, uid, ids, ptype='computed_list_price', context=None):
        """
        Use computed price as default.
        We use old api because somewhere we get wrong convertion between \
        old/new api with context. For eg. with timesheets
        """
        if context is None:
            context = {}
        return super(product_product, self).price_get(
            cr, uid, ids, ptype, context)


class product_template(models.Model):
    _inherit = "product.template"


    # lst_price now cames from computed_list_price
    lst_price = fields.Float(
        related='computed_list_price',
        readonly=True,
        )
    computed_list_price = fields.Float(
        string='Sale Price',
        compute='_get_computed_list_price',
        inverse='_set_prices',
        help='Computed Sale Price. This value depends on "Sale Price Type" an '
        'other parameters. If you set this value, other fields will be '
        'computed automatically.',
        )
    list_price_type = fields.Selection([
        ('manual', 'Manual')],
        string='Sale Price Type',
        required=True,
        default='manual',
        )
    computed_list_price_currency_id = fields.Many2one(
        'res.currency',
        string='Computed List Price Currency',
        compute='get_computed_list_price_currency',
        )

    @api.model
    def _get_price_type(self, price_type):
        price_type = self.env['product.price.type'].search(
            [('field', '=', price_type)], limit=1)
        if not price_type:
            raise Warning(_('No Price type defined for field %s' % (
                price_type)))
        return price_type

    @api.multi
    def get_computed_list_price_currency(self):
        price_type = self._get_price_type('computed_list_price')
        for product in self:
            product.computed_list_price_currency_id = price_type.currency_id

    @api.multi
    @api.depends(
        'list_price_type',
        'list_price',
        )
    def _get_computed_list_price(self):
        _logger.info('Getting Compute List Price for products: "%s"' % (
            self.ids))
        for template in self:
            computed_list_price = template.get_computed_list_price()
            computed_list_price = template._other_computed_rules(
                computed_list_price)
            template.computed_list_price = computed_list_price

    @api.multi
    def _other_computed_rules(self, computed_list_price):
        self.ensure_one()
        return computed_list_price

    @api.multi
    def _set_prices(self):
        _logger.info('Set Prices from "computed_list_price"')
        # send coputed list price because it is lost
        for template in self:
            # fix for integration with margin (if you change replanishment cost
            # for eg, uom price was set with zero (TODO improove this)
            if template.computed_list_price:
                template.set_prices(template.computed_list_price)

    @api.multi
    def set_prices(self, computed_list_price):
        self.ensure_one()
        if self.list_price_type == 'manual':
            self.list_price = computed_list_price

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        return self.list_price

    @api.model
    def _price_get(self, products, ptype='list_price'):
        """
        For price type "computed_list_price" we also add variants price_extra
        """
        res = super(product_template, self)._price_get(products, ptype)
        if ptype == 'computed_list_price':
            for product in products:
                res[product.id] += (
                    product._name == "product.product" and
                    product.price_extra or 0.0)
        return res
