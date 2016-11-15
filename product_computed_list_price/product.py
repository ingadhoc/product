# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    computed_list_price_manual = fields.Float(
        help='Field to store manual computed list price'
    )
    computed_list_price = fields.Float(
        string='Computed Sale Price',
        compute='_get_computed_list_price',
        inverse='_inverse_computed_list_price',
        help='Computed Sale Price. This value depends on "Sale Price Type" an '
        'other parameters. If you set this value, other fields will be '
        'computed automatically.',
    )
    list_price_type = fields.Selection([
        ('manual', 'Manual')],
        # TODO rename to computed_list_price_type
        string='Computed Sale Price Type',
        required=True,
        default='manual',
    )

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
    def _inverse_computed_list_price(self):
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
            self.computed_list_price_manual = computed_list_price

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        return self.computed_list_price_manual
