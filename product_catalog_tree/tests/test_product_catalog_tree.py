##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import sys
from unittest.mock import MagicMock, patch

import odoo
from odoo.fields import Command
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


@tagged("post_install", "-at_install")
class TestProductCatalogTreeOrders(TransactionCase):
    """The catalog list on sale orders and customer invoices, and the action that opens it."""

    def setUp(self):
        super().setUp()
        if odoo.release.version_info[0] < 20:
            # In 19.0 the order models mark the catalog update on the HTTP request, which does not exist in a
            # test (in 20.0 the catalog controller does it)
            for path in (
                "odoo.addons.sale.models.sale_order",
                "odoo.addons.purchase.models.purchase_order",
                "odoo.addons.account.models.account_move",
            ):
                module = sys.modules.get(path)
                if module is not None and hasattr(module, "request"):
                    patcher = patch.object(module, "request", MagicMock())
                    patcher.start()
                    self.addCleanup(patcher.stop)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Catalog list customer"})
        cls.product = cls.env["product.product"].create({"name": "Catalog list product", "list_price": 10.0})
        cls.other_product = cls.env["product.product"].create({"name": "Catalog list other", "list_price": 20.0})

    def _sale_order(self, lines=()):
        if "sale.order" not in self.env:
            self.skipTest("sale is not installed")
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create({"product_id": product.id, "product_uom_qty": qty, **extra})
                    for product, qty, extra in lines
                ],
            }
        )

    def _invoice(self):
        if "account.move" not in self.env:
            self.skipTest("account is not installed")
        return self.env["account.move"].create(
            {"move_type": "out_invoice", "partner_id": self.partner.id, "invoice_date": "2026-01-01"}
        )

    def _catalog(self, order, child_field):
        """The catalog action and the context its rows get, as the "Catalog" button builds them."""
        action = order.with_context(order_id=order.id, child_field=child_field).action_add_from_catalog()
        return action, self.product.with_context(**action["context"])

    def _fresh(self, product, action):
        # the computed catalog values are cached per transaction, not per context: read them again
        self.env.invalidate_all()
        return product.with_context(**action["context"])

    def test_the_action_opens_the_list_first_and_keeps_the_other_views(self):
        order = self._sale_order()
        action, _row = self._catalog(order, "order_line")
        list_view = self.env.ref("product_catalog_tree.product_view_tree_catalog")
        self.assertEqual(action["views"][0], (list_view.id, "list"))
        self.assertIn("kanban", [view_type for _view_id, view_type in action["views"][1:]])
        self.assertEqual(action["context"]["order_id"], order.id)
        self.assertEqual(action["context"]["product_catalog_order_model"], "sale.order")

    def test_the_action_filters_by_the_warehouse_location_of_the_order(self):
        order = self._sale_order()
        if "warehouse_id" not in order._fields:
            self.skipTest("sale_stock is not installed")
        order.warehouse_id = self.env["stock.warehouse"].search([("company_id", "=", order.company_id.id)], limit=1)
        action, _row = self._catalog(order, "order_line")
        self.assertEqual(action["context"]["search_default_location_id"], order.warehouse_id.lot_stock_id.id)

    def test_the_list_is_editable_in_quantity_only_and_cannot_create(self):
        view = self.env.ref("product_catalog_tree.product_view_tree_catalog")
        arch = self.env["product.product"].get_view(view_id=view.id, view_type="list")["arch"]
        self.assertIn('editable="top"', arch)
        self.assertIn('create="false"', arch)
        self.assertIn("product_list_catalog", arch)
        self.assertIn('name="product_catalog_qty"', arch)

    def test_sale_order_plus_adds_one_each_time_and_the_row_shows_it(self):
        order = self._sale_order()
        action, row = self._catalog(order, "order_line")
        self.assertEqual(row.product_catalog_qty, 0)
        row.increase_quantity()
        self.assertEqual(order.order_line.product_uom_qty, 1)
        self._fresh(self.product, action).increase_quantity()
        self.assertEqual(order.order_line.product_uom_qty, 2)
        row = self._fresh(self.product, action)
        self.assertEqual(row.product_catalog_qty, 2)
        self.assertEqual(row.product_catalog_price, 10.0)

    def test_sale_order_writing_the_quantity_sets_it_and_zero_removes_the_line(self):
        order = self._sale_order([(self.other_product, 1, {})])
        action, row = self._catalog(order, "order_line")
        row.write({"product_catalog_qty": 5})
        line = order.order_line.filtered(lambda line: line.product_id == self.product)
        self.assertEqual(line.product_uom_qty, 5)
        self._fresh(self.product, action).write({"product_catalog_qty": 0})
        self.assertFalse(order.order_line.filtered(lambda line: line.product_id == self.product))
        self.assertEqual(order.order_line.product_id, self.other_product)

    def test_sale_order_a_line_in_another_unit_keeps_its_unit_and_adds_one(self):
        """The line is in dozens: ``+`` makes it 3 dozens, not 3 units (24 units become 3)."""
        dozen = self.env.ref("uom.product_uom_dozen")
        order = self._sale_order([(self.product, 2, {"product_uom_id": dozen.id})])
        action, row = self._catalog(order, "order_line")
        self.assertEqual(row.product_catalog_qty, 2)
        row.increase_quantity()
        self.assertEqual(order.order_line.product_uom_id, dozen)
        self.assertEqual(order.order_line.product_uom_qty, 3)

    def test_sale_order_with_several_lines_of_the_product_writes_the_difference(self):
        order = self._sale_order([(self.product, 1, {}), (self.product, 2, {})])
        action, row = self._catalog(order, "order_line")
        self.assertEqual(row.product_catalog_qty, 3)
        row.write({"product_catalog_qty": 5})
        self.assertEqual(sum(order.order_line.mapped("product_uom_qty")), 5)
        self.assertEqual(len(order.order_line), 2)
        self._fresh(self.product, action).write({"product_catalog_qty": 1})
        self.assertEqual(sum(order.order_line.mapped("product_uom_qty")), 1)

    def test_invoice_plus_and_writing_the_quantity(self):
        invoice = self._invoice()
        action, row = self._catalog(invoice, "line_ids")
        self.assertEqual(action["context"]["product_catalog_order_model"], "account.move")
        self.assertEqual(action["views"][0][1], "list")
        row.increase_quantity()
        self.assertEqual(invoice.invoice_line_ids.quantity, 1)
        self._fresh(self.product, action).increase_quantity()
        self.assertEqual(invoice.invoice_line_ids.quantity, 2)
        self._fresh(self.product, action).write({"product_catalog_qty": 7})
        self.assertEqual(invoice.invoice_line_ids.quantity, 7)

    def test_without_an_order_in_the_context_the_row_is_empty_and_the_buttons_do_nothing(self):
        row = self.product
        self.assertEqual(row.product_catalog_qty, 0)
        self.assertEqual(row.product_catalog_price, 0)
        self.assertEqual(row.product_catalog_min_qty, 0)
        row.increase_quantity()
        row.set_catalog_min_qty()

    def test_with_the_model_but_without_the_order_the_row_is_empty(self):
        row = self.product.with_context(product_catalog_order_model="sale.order", child_field="order_line")
        self.assertEqual(row.product_catalog_qty, 0)
        self.assertEqual(row.product_catalog_price, 0)
        row.increase_quantity()
