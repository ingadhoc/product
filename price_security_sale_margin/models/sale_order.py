import json

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
                invisible_fields = arch.xpath(
                    "//field[@name='purchase_price']"
                    "|//field[@name='order_line']//field[@name='margin']"
                    "|//field[@name='order_line']//field[@name='margin_percent']"
                    "|//div[@class='d-flex float-end']"
                )
                for node in invisible_fields:
                    node.set("invisible", "1")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers["invisible"] = True
                    node.set("column_invisible", "1")
                    modifiers["column_invisible"] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
