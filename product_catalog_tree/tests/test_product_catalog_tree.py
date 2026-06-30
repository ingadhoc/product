##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCatalogTree(TransactionCase):
    def test_add_catalog_min_qty_uses_supplier_price(self):
        """The new catalog button adds the product with the vendor's min_qty,
        so the supplier price applies instead of falling back to the cost."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase is not installed")

        vendor = self.env["res.partner"].create({"name": "Vendor Min Qty"})
        product = self.env["product.product"].create({
            "name": "Cable roll 100m",
            "standard_price": 50.0,
            "purchase_ok": True,
            "seller_ids": [(0, 0, {
                "partner_id": vendor.id,
                "price": 99.0,
                "min_qty": 100,
            })],
        })
        order = self.env["purchase.order"].create({"partner_id": vendor.id})
        catalog_product = product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )

        # the vendor minimum quantity is exposed on the catalog row
        self.assertEqual(catalog_product.product_catalog_min_qty, 100)

        # the new button adds the product with the vendor min_qty (mirrors the
        # kanban catalog) instead of a hardcoded 1 like the ``+`` button
        catalog_product.add_catalog_min_qty()
        line = order.order_line.filtered(lambda line: line.product_id == product)
        self.assertEqual(line.product_qty, 100)

        # therefore the vendor price applies, not the product cost (50)
        self.assertEqual(line.price_unit, 99.0)

    def test_increase_quantity_keeps_adding_one(self):
        """The ``+`` button keeps its original behaviour (adds one)."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase is not installed")

        vendor = self.env["res.partner"].create({"name": "Vendor Plus"})
        product = self.env["product.product"].create({
            "name": "Cable roll plus",
            "standard_price": 50.0,
            "purchase_ok": True,
            "seller_ids": [(0, 0, {
                "partner_id": vendor.id,
                "price": 99.0,
                "min_qty": 100,
            })],
        })
        order = self.env["purchase.order"].create({"partner_id": vendor.id})
        catalog_product = product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )

        catalog_product.increase_quantity()
        line = order.order_line.filtered(lambda line: line.product_id == product)
        self.assertEqual(line.product_qty, 1)
