from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestCostReadability(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restricted_user = new_test_user(
            cls.env,
            login="price_security_cost_reader",
            groups="base.group_user,sales_team.group_sale_salesman_all_leads,"
            "stock.group_stock_user,price_security.group_only_view_sale_price",
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Restricted cost product",
                "is_storable": True,
                "list_price": 150.0,
                "standard_price": 100.0,
            }
        )

    def _as_user(self, model):
        return self.env[model].with_user(self.restricted_user)

    def test_fields_get_does_not_offer_the_cost(self):
        """This is what the AI agent and the export dialog read to know what exists"""
        fields = self._as_user("product.product").fields_get()
        for field_name in ("standard_price", "avg_cost", "total_value"):
            self.assertNotIn(field_name, fields)
        self.assertIn("list_price", fields)

    def test_reading_the_cost_returns_nothing(self):
        values = self._as_user("product.product").browse(self.product.id).read(["standard_price"])
        self.assertFalse(values[0]["standard_price"])

    def test_grouping_by_the_cost_is_denied(self):
        with self.assertRaises(AccessError):
            self._as_user("product.product")._read_group([], [], ["standard_price:sum"])

    def test_searching_by_the_cost_is_denied(self):
        with self.assertRaises(AccessError):
            self._as_user("product.product").search_count([("standard_price", ">", 0)])

    def test_ordering_by_the_cost_is_denied(self):
        with self.assertRaises(AccessError):
            self._as_user("product.product").search([], order="standard_price desc")

    def test_exporting_the_cost_is_denied(self):
        with self.assertRaises(AccessError):
            self._as_user("product.product").browse(self.product.id).export_data(["standard_price"])

    def test_stock_move_value_returns_nothing(self):
        self.assertNotIn("value", self._as_user("stock.move").fields_get())
        with self.assertRaises(AccessError):
            self._as_user("stock.move").search_count([("value", ">", 0)])

    def test_product_value_returns_nothing(self):
        """Value Adjustments: the value, and everything derived from it"""
        fields = self._as_user("product.value").fields_get()
        for field_name in ("value", "current_value"):
            self.assertNotIn(field_name, fields)
        with self.assertRaises(AccessError):
            self._as_user("product.value").search_count([("value", ">", 0)])

    def test_sale_price_is_still_readable(self):
        values = self._as_user("product.product").browse(self.product.id).read(["list_price"])
        self.assertEqual(values[0]["list_price"], 150.0)

    def test_unrestricted_user_still_reads_the_cost(self):
        values = self.env["product.product"].browse(self.product.id).read(["standard_price"])
        self.assertEqual(values[0]["standard_price"], 100.0)
