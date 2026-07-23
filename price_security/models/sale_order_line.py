##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_can_modify_prices = fields.Boolean(
        related="product_id.can_modify_prices",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._price_security_settle_discount(vals_list)
        lines.check_discount()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if {"discount", "discount1", "discount2", "discount3", "product_id"} & vals.keys():
            self.check_discount()
        return res

    def _price_security_settle_discount(self, vals_list):
        """Hook for modules that rewire the discount computation (e.g.
        sale_triple_discount) and need to settle it before validation. `self` are the
        lines just created, aligned with `vals_list`."""

    def check_discount(self):
        # Validated after create/write instead of api.constrains, which ran during the
        # create flush and could compare transient not-yet-computed discount values.
        if not self.env.user.has_group("price_security.group_only_view"):
            return True
        for rec in self.filtered(lambda x: not x.product_can_modify_prices):
            self.env.user.check_discount(rec.discount, rec.order_id.pricelist_id.id, so_line=rec)
