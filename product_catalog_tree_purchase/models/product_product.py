##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_catalog_supplier_uom = fields.Char(
        string="Supplier UoM",
        compute="_compute_catalog_supplier_uom",
        readonly=True,
    )

    def _compute_catalog_supplier_uom(self):
        """Unit of the vendor pricelist of the order, only in the catalog of a purchase order."""
        res_model = self.env.context.get("product_catalog_order_model")
        order_id = self.env.context.get("order_id")

        for rec in self:
            rec.product_catalog_supplier_uom = ""

            if res_model == "purchase.order" and order_id:
                order = self.env[res_model].browse(order_id)
                partner = order.partner_id

                if partner:
                    seller = rec.seller_ids.filtered(lambda s: s.partner_id == partner)[:1]

                    if seller and seller.uom_id:
                        rec.product_catalog_supplier_uom = seller.uom_id.name
