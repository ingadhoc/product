##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _update_order_line_info(self, product_id, quantity, **kwargs):
        """When creating a new PO line from the product catalog,
        It doesn't take into accoount the product replenishmt rule form the supplierinfo,
        We recompute after super() to restore the net_price-based value."""
        existing_line = self.order_line.filtered(lambda line: line.product_id.id == product_id)
        result = super()._update_order_line_info(product_id, quantity, **kwargs)
        if not existing_line and quantity > 0:
            pol = self.order_line.filtered(lambda line: line.product_id.id == product_id)
            if pol:
                pol._compute_price_unit_and_date_planned_and_name()
        return result
