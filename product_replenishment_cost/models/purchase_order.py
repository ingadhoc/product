##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_product_price_and_data(self, product):
        """Override to use net_price from replenishment cost rules in catalog.

        This method is called when displaying products in the purchase catalog.
        If a supplier has replenishment cost rules defined (net_price), we use
        that instead of the regular discounted price.
        """
        # Get the default data from parent
        product_infos = super()._get_product_price_and_data(product)

        # Get seller for this product
        params = {"order_id": self}
        seller = product._select_seller(
            partner_id=self.partner_id,
            quantity=None,
            date=self.date_order and self.date_order.date(),
            uom_id=product.uom_id,
            ordered_by="min_qty",
            params=params,
        )

        # If seller has net_price (product.supplierinfo with replenishment rules), use it
        if seller and hasattr(seller, "net_price"):
            product_uom = (seller.product_id or seller.product_tmpl_id).uom_id
            price = seller.net_price

            # Apply currency conversion
            if seller.currency_id != self.currency_id:
                price = seller.currency_id._convert(price, self.currency_id)

            # Apply UOM conversion
            if seller.product_uom_id != product_uom:
                # The net price is expressed in the product's UoM, not in the vendor
                # price's UoM, so we need to convert it to match the displayed UoM.
                price = product_uom._compute_price(price, seller.product_uom_id)

            # Update the price in result
            product_infos.update(price=price)

        return product_infos

    def _update_order_line_info(self, product_id, quantity, *, section_id=False, child_field="order_line", **kwargs):
        """Override to fix price after parent sets it with seller.price."""
        result = super()._update_order_line_info(
            product_id, quantity, section_id=section_id, child_field=child_field, **kwargs
        )

        # If a new line was created (quantity > 0), recompute price to use net_price
        if quantity > 0:
            pol = self.order_line.filtered(
                lambda l: l.product_id.id == product_id and l.get_parent_section_line().id == section_id
            )[:1]  # Take first one

            if pol and pol.selected_seller_id and hasattr(pol.selected_seller_id, "net_price"):
                # Parent set seller.price, but we want seller.net_price
                # Force recompute by triggering the depends
                pol._compute_price_unit_and_date_planned_and_name()

        return result
