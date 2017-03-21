# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api
from openerp.models import Model
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(Model):
    _inherit = 'product.product'

    @api.multi
    # @api.depends('product_tmpl_id.standard_price', 'standard_price')
    def _get_replenishment_cost(self):
        _logger.info(
            'Getting replenishment cost for product ids %s' % self.ids)
        # sacamos esto porque de alguna maenra lo hace recursivo, el rep cost
        # no lo tomamos mas de standar cost
        # for rec in self:
        #     rec.replenishment_cost = rec.standard_price

    replenishment_cost = fields.Float(
        compute=_get_replenishment_cost, store=True,
        digits_compute=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")
