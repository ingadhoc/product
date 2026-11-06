import json

from odoo import api, models

from .sale_order_line import MARGIN_FIELDS


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "price.security.cost.mixin"]

    _price_security_cost_fields = MARGIN_FIELDS

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
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
            if self.env.user.has_group("price_security.group_only_view_sale_price"):
                # the margin block has no field left in it
                for node in arch.xpath("//div[@class='d-flex float-end']"):
                    node.set("invisible", "1")
        return arch, view
