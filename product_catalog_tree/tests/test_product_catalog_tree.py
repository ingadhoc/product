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
            child_field="order_line",
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
            child_field="order_line",
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
            child_field="order_line",
        )

        catalog_product.increase_quantity()
        line = order.order_line.filtered(lambda line: line.product_id == product)
        self.assertEqual(line.product_qty, 1)


@tagged("post_install", "-at_install")
class TestProductCatalogTreeModels(TransactionCase):
    """The list is only offered where it knows how to write."""

    def test_the_list_opens_first_on_sale_orders_and_invoices(self):
        list_view = self.env.ref("product_catalog_tree.product_view_tree_catalog")
        partner = self.env["res.partner"].create({"name": "Catalog list models"})
        records = []
        if "sale.order" in self.env:
            records.append((self.env["sale.order"].create({"partner_id": partner.id}), "order_line"))
        if "account.move" in self.env:
            records.append(
                (self.env["account.move"].create({"move_type": "out_invoice", "partner_id": partner.id}), "line_ids")
            )
        if not records:
            self.skipTest("neither sale nor account is installed")
        for record, child_field in records:
            action = record.with_context(order_id=record.id, child_field=child_field).action_add_from_catalog()
            self.assertEqual(action["views"][0], (list_view.id, "list"), record._name)

    def test_a_quotation_template_keeps_its_own_catalog(self):
        if "sale.order.template" not in self.env:
            self.skipTest("sale_management is not installed")
        list_view = self.env.ref("product_catalog_tree.product_view_tree_catalog")
        template = self.env["sale.order.template"].create({"name": "Catalog list template"})
        action = template.with_context(
            order_id=template.id, child_field="sale_order_template_line_ids"
        ).action_add_from_catalog()
        self.assertNotIn((list_view.id, "list"), action["views"])
        self.assertEqual(action["views"][0][1], "kanban")
