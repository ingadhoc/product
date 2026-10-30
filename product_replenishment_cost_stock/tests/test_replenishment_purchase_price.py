##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from datetime import timedelta

from odoo import Command, fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReplenishmentPurchasePrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.route_buy = cls.warehouse.buy_pull_id.route_id
        cls.route_buy.product_selectable = True
        cls.vendor = cls.env["res.partner"].create({"name": "Replenishment vendor"})
        # Adds 10% plus 5 to the vendor price: 100 -> 115
        cls.cost_rule = cls.env["product.replenishment_cost.rule"].create(
            {
                "name": "Freight",
                "item_ids": [Command.create({"name": "Freight", "percentage_amount": 10.0, "fixed_amount": 5.0})],
            }
        )

    def _create_product(self, seller_price, cost_rule=None):
        return self.env["product.product"].create(
            {
                "name": "Replenished product",
                "is_storable": True,
                "standard_price": 40.0,
                "supplier_taxes_id": [Command.clear()],
                "route_ids": [Command.link(self.route_buy.id)],
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": self.vendor.id,
                            "price": seller_price,
                            "replenishment_cost_rule_id": cost_rule and cost_rule.id,
                        }
                    )
                ],
            }
        )

    def _replenish(self, product):
        self.env["stock.rule"].run(
            [
                self.env["stock.rule"].Procurement(
                    product,
                    1.0,
                    product.uom_id,
                    self.warehouse.lot_stock_id,
                    product.name,
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.warehouse,
                        "date_planned": fields.Datetime.now() + timedelta(days=10),
                    },
                )
            ]
        )
        return self.env["purchase.order.line"].search(
            [("product_id", "=", product.id), ("order_id.state", "=", "draft")]
        )

    def test_replenishment_purchase_price(self):
        """The purchase line a replenishment creates or updates takes the vendor
        net price, the last purchase price without vendor pricelist, or the
        product cost when there is no price."""
        product = self._create_product(seller_price=0.0)
        with self.subTest("new line, vendor without price"):
            # Replenish a product whose vendor has no price
            line = self._replenish(product)
            self.assertEqual(len(line), 1)
            self.assertEqual(line.price_unit, 40.0)
        with self.subTest("updated line, vendor without price"):
            # A second replenishment merges into the same draft line
            line = self._replenish(product)
            self.assertEqual(len(line), 1)
            self.assertEqual(line.product_qty, 2.0)
            self.assertEqual(line.price_unit, 40.0)
        with self.subTest("updated line, vendor price with a cost rule"):
            product = self._create_product(seller_price=100.0, cost_rule=self.cost_rule)
            self._replenish(product)
            # The update takes the net price, not the vendor list price
            line = self._replenish(product)
            self.assertEqual(len(line), 1)
            self.assertEqual(line.product_qty, 2.0)
            self.assertEqual(line.price_unit, 115.0)
        with self.subTest("updated line, no vendor pricelist but a previous purchase"):
            product = self._create_product(seller_price=0.0)
            product.seller_ids.unlink()
            # A confirmed purchase at 70 acts as the vendor price since 20.0
            previous = self.env["purchase.order"].create(
                {
                    "partner_id": self.vendor.id,
                    "order_line": [Command.create({"product_id": product.id, "product_qty": 1.0, "price_unit": 70.0})],
                }
            )
            previous.button_confirm()
            line = self._replenish(product)
            self.assertEqual(line.price_unit, 70.0)
            # The update keeps the last purchase price instead of the product cost
            line = self._replenish(product)
            self.assertEqual(len(line), 1)
            self.assertEqual(line.product_qty, 2.0)
            self.assertEqual(line.price_unit, 70.0)
