from odoo import api, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.onchange("compute_price")
    def _onchange_compute_price(self):
        """Surcharge rules round by default to the price precision, unless a
        rounding was already set. Discount rules are left as in Odoo: a rounded
        discount is no longer a plain discount, and sales stop showing it."""
        super()._onchange_compute_price()
        if self.compute_price == "markup" and not self.price_round:
            self.price_round = 10 ** -self.env["decimal.precision"].sudo().precision_get("Product Price")
