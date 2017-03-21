# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = "product.template"

    sale_margin = fields.Float(
        'Planned Price Sale margin %',
        digits=dp.get_precision('Discount'),
    )
    sale_surcharge = fields.Float(
        'Planned Price Sale surcharge',
        digits=dp.get_precision('Product Price')
    )
    list_price_type = fields.Selection(
        selection_add=[('by_margin', 'By Margin')],
    )
    replenishment_cost_copy = fields.Float(
        related='replenishment_cost'
        # related='product_variant_ids.replenishment_cost'
    )

    @api.multi
    @api.depends(
        'sale_margin',
        'sale_surcharge',
        'replenishment_cost',
    )
    def _get_computed_list_price(self):
        """Only to update depends"""
        return super(product_template, self)._get_computed_list_price()

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'by_margin':
            _logger.info('Get computed_list_price for "by_margin" type')
            print 'bbbbbbbbbb', self
            return self.replenishment_cost * \
                (1 + self.sale_margin / 100.0) + \
                self.sale_surcharge
        return super(product_template, self).get_computed_list_price()
