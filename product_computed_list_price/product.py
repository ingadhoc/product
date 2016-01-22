# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = "product.template"

    computed_list_price = fields.Float(
        string='Computed Sale Price',
        compute='_get_computed_list_price',
        inverse='_set_prices',
        help='This value depends on "Sale Price Type" an '
        'other parameters. If you set this value, other fields will be '
        'computed automatically.',
        )
    list_price_type = fields.Selection([
        ('manual', 'Manual')],
        string='Sale Price Type',
        required=True,
        default='manual',
        )

    @api.multi
    @api.depends(
        'list_price_type',
        'list_price',
        )
    def _get_computed_list_price(self):
        for template in self:
            computed_list_price = template.get_computed_list_price()
            _logger.info('Compute Lis Price calculated = "%s"' % (
                computed_list_price))
            template.computed_list_price = computed_list_price

    @api.multi
    def _set_prices(self):
        _logger.info('Set Prices from "computed_list_price"')
        for template in self:
            template.set_prices()

    @api.multi
    def set_prices(self):
        self.ensure_one()
        if self.list_price_type == 'manual':
            _logger.info('Set Prices from "computed_list_price" type "manual"')
            self.list_price = self.computed_list_price

    @api.multi
    def get_computed_list_price(self):
        _logger.info('Get computed_list_price')
        self.ensure_one()
        return self.list_price
