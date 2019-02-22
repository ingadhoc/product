##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def price_compute(
            self, price_type, uom=False, currency=False, company=False):
        """
        We do this so that if someone wants to force the calculated price
        be based on the planned, you can do it by sending use_planned_price
        in the context
        """
        if self._context.get(
                'use_planned_price') and price_type == 'list_price':
            price_type = 'computed_list_price'
        return super(
            ProductProduct, self).price_compute(
            price_type, uom=uom, currency=currency, company=company)
