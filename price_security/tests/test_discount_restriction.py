from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestDiscountRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("base.user_root").group_ids += cls.env.ref("sale.group_discount_per_so_line")
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Discount Restriction Pricelist",
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
                "name": "Discount Restriction Customer",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Discount Restriction Product",
                "type": "consu",
                "list_price": 100.0,
            }
        )
        cls.seller = new_test_user(
            cls.env,
            login="price_security_seller",
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

    def _assert_restriction_blocks(self, apply_discount):
        if self.deferred_check:
            apply_discount()
            self.order.with_user(self.seller).action_confirm()
            self.assertEqual(self.order.state, "draft")
            self.assertIn(
                self.env.ref("sale_exception_price_security.discount_restriction"),
                self.order.exception_ids,
            )
        else:
            with self.assertRaises(UserError):
                apply_discount()

    def _create_line(self, **extra_vals):
        vals = {
            "order_id": self.order.id,
            "product_id": self.product.id,
            "product_uom_qty": 1,
            **extra_vals,
        }
        return self.env["sale.order.line"].with_user(self.seller).create(vals)

    def _apply_extra_discount(self, line, extra):
        """Apply a manual discount on top of the 30% pricelist discount, through the
        channel available in the installed discount stack: with sale_triple_discount
        `discount` becomes readonly (and sale_triple_discount_lock forces discount1 to
        the pricelist discount), so discount3 is the manual channel there."""
        if "discount3" in line._fields:
            line.with_user(self.seller).write({"discount3": extra})
            # combined discount: 100 * (1 - 0.7 * (1 - extra / 100))
            return 100 - 70.0 * (1 - extra / 100.0)
        line.with_user(self.seller).write({"discount": 30.0 + extra})
        return 30.0 + extra

    def test_create_without_discount_keeps_pricelist_discount(self):
        # Lines created without explicit discount (e.g. from the product catalog)
        # must end up with the pricelist discount and pass the restriction check.
        line = self._create_line()
        self.assertAlmostEqual(line.discount, 30.0, places=2)

    def test_discount_above_restriction_is_blocked(self):
        line = self._create_line()
        # extra 25% -> net discount over the 10% allowed
        self._assert_restriction_blocks(lambda: self._apply_extra_discount(line, 25.0))

    def test_discount_within_restriction_is_allowed(self):
        line = self._create_line()
        expected = self._apply_extra_discount(line, 10.0)
        self.assertAlmostEqual(line.discount, expected, places=2)

    def test_generic_restriction_wins_over_another_pricelist_row(self):
        """A row without pricelist is the default for pricelists with no row of their
        own, instead of borrowing the range of an unrelated pricelist."""
        other_pricelist = self.env["product.pricelist"].create({"name": "Other Pricelist"})
        self.env["res.users.discount_restriction"].create(
            {
                "user_id": self.seller.id,
                "pricelist_id": False,
                "min_discount": 0.0,
                "max_discount": 50.0,
            }
        )
        self.order.pricelist_id = other_pricelist
        line = self._create_line()
        # 40% is outside the 0-10 range of the `cls.pricelist` row and inside the
        # 0-50 of the generic one: it must be the generic one that applies.
        # Asserted on check_discount itself: with sale_exception_price_security the
        # write goes through either way, so writing and reading back proves nothing.
        error = self.seller.check_discount(40.0, other_pricelist.id, so_line=line, do_not_raise=True)
        self.assertFalse(error, f"the generic restriction should allow 40%, got: {error}")

    def test_inherited_range_names_its_source_pricelist(self):
        """When the range comes from another pricelist's row, the error says so:
        the range is not the one of the pricelist on screen."""
        other_pricelist = self.env["product.pricelist"].create({"name": "Other Pricelist"})
        self.order.pricelist_id = other_pricelist
        line = self._create_line()
        error = self.seller.check_discount(40.0, other_pricelist.id, so_line=line, do_not_raise=True)
        self.assertTrue(error)
        self.assertIn(self.pricelist.name, error)
        self.assertIn(other_pricelist.name, error)

    def test_not_allowed_pricelist_error_names_the_pricelist(self):
        """The blocking message names the pricelist and the field to configure,
        instead of the generic "according to the restrictions configured"."""
        # Without the pricelist feature the partner property stays empty and
        # check_allowed_pricelist short-circuits, so there is nothing to assert.
        self.env["res.config.settings"].create({"group_product_pricelist": True}).execute()
        self.partner.specific_property_product_pricelist = self.pricelist
        other_pricelist = self.env["product.pricelist"].create({"name": "Not Allowed Pricelist"})
        with self.assertRaises(UserError) as caught:
            self.env["sale.order"].with_user(self.seller).create(
                {
                    "partner_id": self.partner.id,
                    "pricelist_id": other_pricelist.id,
                }
            )
        message = str(caught.exception)
        self.assertIn(other_pricelist.name, message)
        self.assertIn(self.pricelist.name, message)
