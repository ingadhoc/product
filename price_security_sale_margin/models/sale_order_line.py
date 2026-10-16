import json

from odoo import api, models

# the margin exposes the cost by subtraction, so it is restricted along with it
MARGIN_FIELDS = ("purchase_price", "margin", "margin_percent")


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "price.security.cost.mixin"]

    _price_security_cost_fields = MARGIN_FIELDS

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        """the arch below depends on the group, so it can not be shared"""
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + (self.env.user.has_group("price_security.group_only_view"),)

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "list":
            if self.env.user.has_group("price_security.group_only_view"):
                readonly_fields = (
                    arch.xpath("//field[@name='purchase_price']")
                    + arch.xpath("//field[@name='margin']")
                    + arch.xpath("//field[@name='margin_percent']")
                )
                for node in readonly_fields:
                    node.set("readonly", "1")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers["readonly"] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
