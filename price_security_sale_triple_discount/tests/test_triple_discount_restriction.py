from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestTripleDiscountRestriction(TransactionCase):
    """Reproduces adding products from the catalog view as a user with discount
    restrictions: the line is created without explicit discount values and the
    pricelist discount must settle before the restriction check runs.

    Manual discounts are applied through discount3: discount is readonly with
    sale_triple_discount, and sale_triple_discount_lock (if installed) forces
    discount1 back to the pricelist discount."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("base.user_root").group_ids += cls.env.ref("sale.group_discount_per_so_line")
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Triple Discount Restriction Pricelist",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "percentage",
                            "percent_price": 30.0,
                        }
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Triple Discount Restriction Customer",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Triple Discount Restriction Product",
                "type": "consu",
                "list_price": 100.0,
            }
        )
        cls.seller = new_test_user(
            cls.env,
            login="triple_discount_seller",
            groups="sales_team.group_sale_salesman,price_security.group_only_view",
        )
        cls.env["res.users.discount_restriction"].create(
            {
                "user_id": cls.seller.id,
                "pricelist_id": cls.pricelist.id,
                "min_discount": 0.0,
                "max_discount": 10.0,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "user_id": cls.seller.id,
            }
        )
        # sale_exception_price_security (auto-installed with sale_exception) disables
        # the immediate UserError and defers enforcement to a blocking sale exception
        # on order confirmation.
        cls.deferred_check = (
            cls.env["ir.module.module"].search([("name", "=", "sale_exception_price_security")]).state == "installed"
        )

    def _create_line(self, **extra_vals):
        vals = {
            "order_id": self.order.id,
            "product_id": self.product.id,
            "product_uom_qty": 1,
            **extra_vals,
        }
        return self.env["sale.order.line"].with_user(self.seller).create(vals)

    def test_catalog_style_create_keeps_pricelist_discount(self):
        line = self._create_line()
        self.assertAlmostEqual(line.discount, 30.0, places=2)
        self.assertAlmostEqual(line.discount1, 30.0, places=2)

    def test_extra_discount_within_restriction_is_allowed(self):
        line = self._create_line()
        # extra 10% on discount3 -> combined 37%, net 7% within the allowed 10%
        line.with_user(self.seller).write({"discount3": 10.0})
        self.assertAlmostEqual(line.discount, 37.0, places=2)

    def test_extra_discount_above_restriction_is_blocked(self):
        line = self._create_line()
        # extra 25% on discount3 -> combined 47.5%, net 17.5% over the allowed 10%
        if self.deferred_check:
            line.with_user(self.seller).write({"discount3": 25.0})
            self.order.with_user(self.seller).action_confirm()
            self.assertEqual(self.order.state, "draft")
            self.assertIn(
                self.env.ref("sale_exception_price_security.discount_restriction"),
                self.order.exception_ids,
            )
        else:
            with self.assertRaises(UserError):
                line.with_user(self.seller).write({"discount3": 25.0})
