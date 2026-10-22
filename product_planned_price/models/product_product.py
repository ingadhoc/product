##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        """
        We do this so that if someone wants to force the calculated price
        be based on the planned, you can do it by sending use_planned_price
        in the context
        """
        if self.env.context.get("use_planned_price") and price_type == "list_price":
            price_type = "computed_list_price"
        return super()._price_compute(price_type, uom=uom, currency=currency, company=company, date=date)
