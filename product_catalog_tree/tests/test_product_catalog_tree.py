<<<<<<< HEAD
||||||| MERGE BASE
=======
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCatalogTree(TransactionCase):
    def test_set_catalog_min_qty_uses_supplier_price(self):
        """The new catalog button sets the product to the vendor's min_qty,
        so the supplier price applies instead of falling back to the cost."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase is not installed")

        vendor = self.env["res.partner"].create({"name": "Vendor Min Qty"})
        product = self.env["product.product"].create(
            {
                "name": "Cable roll 100m",
                "standard_price": 50.0,
                "purchase_ok": True,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": vendor.id,
                            "price": 99.0,
                            "min_qty": 100,
                        },
                    )
                ],
            }
        )
        order = self.env["purchase.order"].create({"partner_id": vendor.id})
        catalog_product = product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )

        # the vendor minimum quantity is exposed on the catalog row
        self.assertEqual(catalog_product.product_catalog_min_qty, 100)

        # the button sets the product to the vendor min_qty instead of a
        # hardcoded 1 like the ``+`` button
        catalog_product.set_catalog_min_qty()
        line = order.order_line.filtered(lambda line: line.product_id == product)
        self.assertEqual(line.product_qty, 100)

        # therefore the vendor price applies, not the product cost (50)
        self.assertEqual(line.price_unit, 99.0)

    def test_set_catalog_min_qty_replaces_existing_qty(self):
        """When the product is already on the order the button replaces the
        quantity with the vendor min_qty (it does not add one)."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase is not installed")

        vendor = self.env["res.partner"].create({"name": "Vendor Replace"})
        product = self.env["product.product"].create(
            {
                "name": "Cable roll replace",
                "standard_price": 50.0,
                "purchase_ok": True,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": vendor.id,
                            "price": 99.0,
                            "min_qty": 100,
                        },
                    )
                ],
            }
        )
        order = self.env["purchase.order"].create({"partner_id": vendor.id})
        catalog_product = product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )

        # the product already has a quantity below the vendor minimum
        catalog_product.increase_quantity()
        line = order.order_line.filtered(lambda line: line.product_id == product)
        self.assertEqual(line.product_qty, 1)

        # clicking the truck replaces the quantity with the vendor min_qty
        # (instead of adding one, which was the bug), so the vendor price applies
        catalog_product.set_catalog_min_qty()
        self.assertEqual(line.product_qty, 100)
        self.assertEqual(line.price_unit, 99.0)

    def test_increase_quantity_keeps_adding_one(self):
        """The ``+`` button keeps its original behaviour (adds one)."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase is not installed")

        vendor = self.env["res.partner"].create({"name": "Vendor Plus"})
        product = self.env["product.product"].create(
            {
                "name": "Cable roll plus",
                "standard_price": 50.0,
                "purchase_ok": True,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": vendor.id,
                            "price": 99.0,
                            "min_qty": 100,
                        },
                    )
                ],
            }
        )
        order = self.env["purchase.order"].create({"partner_id": vendor.id})
        catalog_product = product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )

        catalog_product.increase_quantity()
        line = order.order_line.filtered(lambda line: line.product_id == product)
        self.assertEqual(line.product_qty, 1)

    def test_increase_quantity_on_repair_order_does_not_crash(self):
        """Regression test: unlike sale/purchase orders, repair.order does not
        expose an ``order_line`` field (it uses ``move_ids``), which used to
        crash the catalog's ``+`` button with an AttributeError."""
        if "repair.order" not in self.env:
            self.skipTest("repair is not installed")

        product_to_repair = self.env["product.product"].create({"name": "Broken widget"})
        component = self.env["product.product"].create({"name": "Spare part"})
        repair = self.env["repair.order"].create({"product_id": product_to_repair.id})
        catalog_product = component.with_context(
            product_catalog_order_model="repair.order",
            order_id=repair.id,
        )

        catalog_product.increase_quantity()

        move = repair.move_ids.filtered(lambda m: m.product_id == component)
        self.assertEqual(move.product_uom_qty, 1)

>>>>>>> FORWARD PORTED
