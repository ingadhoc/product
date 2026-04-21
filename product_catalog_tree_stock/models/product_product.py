##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import json

from lxml import etree
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_catalog_supplier_uom = fields.Char(
        string="Supplier UoM",
        compute="_compute_catalog_supplier_uom",
        readonly=True,
    )

    def _compute_catalog_supplier_uom(self):
        """Obtener la UoM del proveedor si estamos en una orden de compra"""
        res_model = self.env.context.get("product_catalog_order_model")
        order_id = self.env.context.get("order_id")

        for rec in self:
            rec.product_catalog_supplier_uom = ""

            # Solo aplicar en órdenes de compra
            if res_model == "purchase.order" and order_id:
                order = self.env[res_model].browse(order_id)
                partner = order.partner_id

                if partner:
                    # Buscar el seller_id para este proveedor
                    seller = rec.seller_ids.filtered(lambda s: s.partner_id == partner)[:1]

                    if seller and seller.product_uom_id:
                        rec.product_catalog_supplier_uom = seller.product_uom_id.name

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)

        catalog_tree_view_id = self.env.ref("product_catalog_tree.product_view_tree_catalog").id

        if view_id and view_id == catalog_tree_view_id:
            doc = etree.XML(res["arch"])

            always_hide = [
                "website_id",
                "website_sequence",
                "website_published",
                "product_brand_id",
                "product_tag_ids",
                "categ_id",
                "detailed_type",
                "type",
                "currency_id",
            ]

            for field_name in always_hide:
                for node in doc.xpath(f"//field[@name='{field_name}']"):
                    node.set("column_invisible", "1")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers["column_invisible"] = True
                    node.set("modifiers", json.dumps(modifiers))

            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
