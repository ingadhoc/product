import json

from odoo import api, models
from odoo.tools.translate import get_translation


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("margin")
    @api.depends_context("uid")
    def _compute_extra_total_fields(self):
        super()._compute_extra_total_fields()
        if not self.env.user.has_group("price_security.group_only_view_sale_price"):
            return
        lang = self.env.lang or "en_US"
        for order in self:
            if not order.margin:
                continue
            # same label sale_margin adds, translated in its own module
            label = get_translation(
                "sale_margin" if lang != "en_US" else "base",
                lang,
                "Margin (%(percent).0f%%)",
                {"percent": order.margin_percent * 100},
            )
            groups = order.extra_total_fields
            for group in groups:
                group["lines"] = [
                    line
                    for line in group.get("lines", [])
                    if not (line.get("label") == label and line.get("value") == order.margin)
                ]
            order.extra_total_fields = groups

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
                )
                for node in invisible_fields:
                    node.set("invisible", "1")
                    node.set("column_invisible", "1")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers["invisible"] = True
                    node.set("column_invisible", "1")
                    modifiers["column_invisible"] = True
                    node.set("modifiers", json.dumps(modifiers))
                    node.attrib.pop("optional", None)
        return arch, view
