from lxml import etree
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderViewReadonly(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.only_view_user = new_test_user(
            cls.env,
            login="price_security_only_view_user",
            groups="base.group_user,sales_team.group_sale_salesman,price_security.group_only_view",
        )

    def _get_order_line_nodes(self, user, view_type, field_name):
        arch = self.env["sale.order"].with_user(user).get_view(view_type="form")["arch"]
        arch = etree.fromstring(arch)
        return arch.xpath("//field[@name='order_line']/%s//field[@name='%s']" % (view_type, field_name))

    def test_order_line_price_and_taxes_readonly(self):
        """Users that can only view prices must not be able to edit the unit
        price nor the taxes of the sale order lines
        """
        for field_name in ("price_unit", "tax_ids"):
            for view_type in ("list", "form"):
                nodes = self._get_order_line_nodes(self.only_view_user, view_type, field_name)
                self.assertTrue(nodes, "%s is expected on the order line %s view" % (field_name, view_type))
                for node in nodes:
                    self.assertIn(
                        "product_can_modify_prices == False",
                        node.get("readonly"),
                        "%s must be readonly on the order line %s view" % (field_name, view_type),
                    )

    def test_order_line_core_readonly_is_kept(self):
        """The readonly condition core sets (invoiced lines, downpayments) must
        survive for view only users, otherwise they could edit more than a normal user
        """
        for field_name in ("price_unit", "tax_ids"):
            for view_type in ("list", "form"):
                core_nodes = self._get_order_line_nodes(self.env.user, view_type, field_name)
                nodes = self._get_order_line_nodes(self.only_view_user, view_type, field_name)
                for core_node, node in zip(core_nodes, nodes, strict=True):
                    core_readonly = core_node.get("readonly")
                    if not core_readonly:
                        continue
                    self.assertIn(
                        core_readonly,
                        node.get("readonly"),
                        "core readonly of %s must be kept on the order line %s view" % (field_name, view_type),
                    )

    def test_order_line_not_readonly_without_only_view_group(self):
        """Users that are not in group_only_view must not get the price security readonly"""
        user = new_test_user(
            self.env,
            login="price_security_regular_user",
            groups="base.group_user,sales_team.group_sale_salesman",
        )
        for field_name in ("price_unit", "tax_ids"):
            for view_type in ("list", "form"):
                for node in self._get_order_line_nodes(user, view_type, field_name):
                    self.assertNotIn("product_can_modify_prices", node.get("readonly") or "")
