from lxml import etree
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestCostVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restricted_user = new_test_user(
            cls.env,
            login="price_security_stock_user",
            groups="base.group_user,stock.group_stock_manager,price_security.group_only_view_sale_price",
        )

    def _get_list_arch(self, model, view_xmlid):
        view = self.env.ref(view_xmlid)
        arch = self.env[model].with_user(self.restricted_user).get_view(view.id, "list")["arch"]
        return etree.fromstring(arch)

    def _assert_columns_hidden(self, arch, field_names):
        for field_name in field_names:
            nodes = arch.xpath("//field[@name='%s']" % field_name)
            self.assertTrue(nodes, "%s is expected on the view" % field_name)
            for node in nodes:
                # column_invisible is what actually drops the column: invisible
                # would leave the header, the optional toggle and the footer sum
                self.assertEqual(
                    node.get("column_invisible"),
                    "1",
                    "%s must be hidden for users that only see the sale price" % field_name,
                )

    def test_stock_report_hides_cost_columns(self):
        """The stock report (Inventory > Reporting > Stock) must not leak the
        valuation columns that stock_account adds to it
        """
        arch = self._get_list_arch("product.product", "stock.product_product_stock_tree")
        self._assert_columns_hidden(arch, ("avg_cost", "total_value"))
        # the secondary currency ones only exist with stock_currency_valuation
        in_currency = [
            f for f in ("avg_cost_in_currency", "total_value_in_currency") if f in self.env["product.product"]._fields
        ]
        self._assert_columns_hidden(arch, in_currency)

    def test_quant_list_hides_value(self):
        arch = self._get_list_arch("stock.quant", "stock.view_stock_quant_tree_editable")
        self._assert_columns_hidden(arch, ("value",))
        if "secondary_value" in self.env["stock.quant"]._fields:
            self._assert_columns_hidden(arch, ("secondary_value",))

    def test_lot_form_hides_cost(self):
        view = self.env.ref("stock.view_production_lot_form")
        arch = self.env["stock.lot"].with_user(self.restricted_user).get_view(view.id, "form")["arch"]
        arch = etree.fromstring(arch)
        for field_name in ("total_value", "avg_cost", "standard_price"):
            nodes = arch.xpath("//field[@name='%s']" % field_name)
            self.assertTrue(nodes, "%s is expected on the lot form" % field_name)
            for node in nodes:
                self.assertEqual(node.get("invisible"), "1")

    def test_unrestricted_user_still_sees_cost(self):
        arch = etree.fromstring(
            self.env["product.product"].get_view(self.env.ref("stock.product_product_stock_tree").id, "list")["arch"]
        )
        nodes = arch.xpath("//field[@name='total_value']")
        self.assertTrue(nodes)
        self.assertNotEqual(nodes[0].get("column_invisible"), "1")
