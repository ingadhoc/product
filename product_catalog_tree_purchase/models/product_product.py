##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_catalog_supplier_uom = fields.Char(
        string="Supplier UoM",
        compute="_compute_catalog_supplier_uom",
    )

    @api.depends_context("product_catalog_order_model", "order_id")
    def _compute_catalog_supplier_uom(self):
        """Unit of the vendor pricelist of the order, only in the catalog of a purchase order."""
        self.product_catalog_supplier_uom = ""
        res_model = self.env.context.get("product_catalog_order_model")
        order_id = self.env.context.get("order_id")
        if res_model != "purchase.order" or not order_id:
            return

        order = self.env[res_model].browse(order_id)
        if not order.partner_id:
            return

        date = fields.Date.context_today(order, timestamp=order.date_order)
        for rec in self:
            # same seller that purchase uses for the price of the catalog
            seller_info = rec._select_seller(
                partner_id=order.partner_id,
                quantity=None,
                date=date,
                ordered_by="min_qty",
                params={"order_id": order},
            )
            if seller_info:
                rec.product_catalog_supplier_uom = seller_info["uom_id"].name
