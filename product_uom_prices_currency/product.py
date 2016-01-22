# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, _, api
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):

    """"""

    _inherit = 'product.template'

    list_price_type = fields.Selection(
        selection_add=[('by_uom_currency', 'By UOM and Currency')],
        )

    @api.multi
    def set_prices(self):
        self.ensure_one()
        if self.list_price_type == 'by_uom_currency':
            if not self.other_currency_id:
                raise Warning(_(
                    'You must configure "Other Currency" for product %s' % (
                        self.name)))
            _logger.info(
                'Set Prices from "computed_list_price" type "by_uom_currency"')
            self.other_currency_list_price = self._get_price_type(
                'computed_list_price').currency_id.compute(
                self.computed_list_price, self.other_currency_id)
        else:
            return super(product_template, self).set_prices()

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        if self.list_price_type == 'by_uom_currency':
            _logger.info(
                'Get computed_list_price "by_uom_currency"')
            uom_price = self.get_uom_price() or self.other_currency_list_price
            return self.other_currency_id.compute(
                uom_price,
                self._get_price_type('computed_list_price').currency_id)
        return super(product_template, self).get_computed_list_price()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
