from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    item_count = fields.Integer(compute="_compute_item_count")

    def _compute_item_count(self):
        counts = dict(
            self.env["product.pricelist.item"]._read_group(
                [("pricelist_id", "in", self.ids)], ["pricelist_id"], ["__count"]
            )
        )
        for pricelist in self:
            pricelist.item_count = counts.get(pricelist, 0)
