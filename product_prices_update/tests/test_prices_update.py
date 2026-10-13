from odoo.exceptions import AccessError, UserError
from odoo.fields import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductPricesUpdate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.template"].create(
            {"name": "Prices update A", "list_price": 100.0, "standard_price": 50.0}
        )
        cls.product_b = cls.env["product.template"].create(
            {"name": "Prices update B", "list_price": 200.0, "standard_price": 80.0}
        )
        cls.product_c = cls.env["product.template"].create(
            {"name": "Prices update C", "list_price": 300.0, "standard_price": 120.0}
        )
        cls.selected = cls.product_a | cls.product_b
        cls.internal = cls._create_user("prices_update_internal", ["base.group_user"])

    @classmethod
    def _create_user(cls, login, groups):
        return (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [Command.set([cls.env.ref(xmlid).id for xmlid in groups])],
                }
            )
        )

    def _wizard(self, user=None, **values):
        values = {"price_type": "list_price", **values}
        wizards = self.env["product.prices_update_wizard"]
        # Other modules can require extra groups to write products (e.g. product_management_group),
        # so the functional flow runs as superuser; the access of regular users has its own test.
        return (wizards.with_user(user) if user else wizards.sudo()).create(values)

    def _change_prices(self, wizard, products=None):
        products = self.selected if products is None else products
        return wizard.with_context(active_ids=products.ids).change_prices()

    def test_calc_new_price(self):
        calc = self.env["product.prices_update_wizard"].calc_new_price
        self.assertAlmostEqual(calc(100.0, 0.1, 0.0, 0.0), 110.0)
        self.assertAlmostEqual(calc(100.0, -0.2, 0.0, 0.0), 80.0)
        self.assertAlmostEqual(calc(100.0, None, None, None), 100.0)
        self.assertAlmostEqual(calc(104.4, 0.0, 0.0, 5.0), 105.0)

    def test_calc_new_price_rounds_before_adding_the_surcharge(self):
        calc = self.env["product.prices_update_wizard"].calc_new_price
        self.assertAlmostEqual(calc(103.0, 0.0, -0.01, 10.0), 99.99)
        self.assertAlmostEqual(calc(100.0, 0.1, -0.01, 10.0), 109.99)

    def test_change_the_sale_price_of_the_selected_products_only(self):
        self._change_prices(self._wizard(price_discount=0.1))
        self.assertAlmostEqual(self.product_a.list_price, 110.0)
        self.assertAlmostEqual(self.product_b.list_price, 220.0)
        self.assertAlmostEqual(self.product_c.list_price, 300.0)
        self.assertAlmostEqual(self.product_a.standard_price, 50.0)

    def test_change_the_cost_price(self):
        self._change_prices(self._wizard(price_type="standard_price", price_surcharge=5.0))
        self.assertAlmostEqual(self.product_a.standard_price, 55.0)
        self.assertAlmostEqual(self.product_b.standard_price, 85.0)
        self.assertAlmostEqual(self.product_a.list_price, 100.0)

    def test_it_needs_at_least_one_selected_product(self):
        with self.assertRaises(UserError):
            self._change_prices(self._wizard(price_discount=0.1), products=self.env["product.template"])

    def test_check_before_changing_opens_the_result_without_changing_prices(self):
        action = self._change_prices(self._wizard(price_discount=0.1, price_surcharge=-1.0, check=True))
        self.assertEqual(action["res_model"], "product.prices_update_wizard_result")
        self.assertEqual(action["context"]["product_tmpl_ids"], self.selected.ids)
        self.assertEqual(action["context"]["price_type"], "list_price")
        self.assertAlmostEqual(self.product_a.list_price, 100.0)
        result = self.env["product.prices_update_wizard_result"].sudo().with_context(**action["context"])
        details = result.create({}).detail_ids
        self.assertEqual(details.product_tmpl_id, self.selected)
        by_product = {line.product_tmpl_id: line for line in details}
        self.assertAlmostEqual(by_product[self.product_a].old_price, 100.0)
        self.assertAlmostEqual(by_product[self.product_a].new_price, 109.0)
        self.assertAlmostEqual(by_product[self.product_b].new_price, 219.0)

    def test_confirm_applies_the_prices_edited_in_the_result(self):
        action = self._change_prices(self._wizard(price_discount=0.1, check=True))
        result = self.env["product.prices_update_wizard_result"].sudo().with_context(**action["context"]).create({})
        line_a = result.detail_ids.filtered(lambda line: line.product_tmpl_id == self.product_a)
        line_a.new_price = 123.0
        result.confirm()
        self.assertAlmostEqual(self.product_a.list_price, 123.0)
        self.assertAlmostEqual(self.product_b.list_price, 220.0)
        self.assertAlmostEqual(self.product_c.list_price, 300.0)

    def test_the_wizard_action_is_bound_to_the_product_list(self):
        action = self.env.ref("product_prices_update.action_update_prices_wizard")
        self.assertEqual(action.binding_model_id.model, "product.template")
        self.assertEqual(action.binding_view_types, "list")

    def test_internal_users_open_the_wizard_but_cannot_write_prices(self):
        wizard = self._wizard(user=self.internal, price_discount=0.1)
        with self.assertRaises(AccessError):
            self._change_prices(wizard)
        self.assertAlmostEqual(self.product_a.list_price, 100.0)
        result = self.env["product.prices_update_wizard_result"].with_user(self.internal).create({})
        self.assertFalse(result.detail_ids)

    def _open_result(self, action):
        return self.env["product.prices_update_wizard_result"].sudo().with_context(**action["context"]).create({})

    def test_check_before_changing_works_on_the_cost_price(self):
        action = self._change_prices(self._wizard(price_type="standard_price", price_surcharge=5.0, check=True))
        self.assertEqual(action["context"]["price_type"], "standard_price")
        result = self._open_result(action)
        line_a = result.detail_ids.filtered(lambda line: line.product_tmpl_id == self.product_a)
        self.assertAlmostEqual(line_a.old_price, 50.0)
        self.assertAlmostEqual(line_a.new_price, 55.0)
        self.assertAlmostEqual(self.product_a.standard_price, 50.0)
        result.confirm()
        self.assertAlmostEqual(self.product_a.standard_price, 55.0)
        self.assertAlmostEqual(self.product_b.standard_price, 85.0)
        self.assertAlmostEqual(self.product_a.list_price, 100.0)

    def test_check_before_changing_applies_the_rounding_and_the_surcharge(self):
        action = self._change_prices(
            self._wizard(price_discount=0.04, price_round=10.0, price_surcharge=-0.01, check=True)
        )
        self.assertAlmostEqual(action["context"]["price_round"], 10.0)
        self.assertAlmostEqual(action["context"]["price_surcharge"], -0.01)
        result = self._open_result(action)
        by_product = {line.product_tmpl_id: line for line in result.detail_ids}
        self.assertAlmostEqual(by_product[self.product_a].new_price, 99.99)
        self.assertAlmostEqual(by_product[self.product_b].new_price, 209.99)
        result.confirm()
        self.assertAlmostEqual(self.product_a.list_price, 99.99)
        self.assertAlmostEqual(self.product_b.list_price, 209.99)
