from lxml import etree
from odoo.tests import TransactionCase, new_test_user, tagged

MARGIN_FIELDS = ("purchase_price", "margin", "margin_percent")


@tagged("post_install", "-at_install")
class TestMarginVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = new_test_user(
            cls.env,
            login="pssm_salesman",
            groups="base.group_user,sales_team.group_sale_salesman",
        )
        cls.only_view_user = new_test_user(
            cls.env,
            login="pssm_only_view",
            groups="base.group_user,sales_team.group_sale_salesman,price_security.group_only_view",
        )
        cls.only_sale_price_user = new_test_user(
            cls.env,
            login="pssm_only_sale_price",
            groups="base.group_user,sales_team.group_sale_salesman,price_security.group_only_view_sale_price",
        )

    def _order_form_margin_nodes(self, user):
        view = self.env.ref("sale.view_order_form")
        arch = etree.fromstring(self.env["sale.order"].with_user(user).get_view(view.id, "form")["arch"])
        nodes = {}
        for field_name in MARGIN_FIELDS:
            found = arch.xpath("//field[@name='order_line']//field[@name='%s']" % field_name)
            self.assertTrue(found, "%s is expected on the order lines" % field_name)
            nodes[field_name] = found
        return nodes

    def test_salesman_keeps_margin_fields(self):
        for field_name, nodes in self._order_form_margin_nodes(self.salesman).items():
            for node in nodes:
                self.assertNotEqual(node.get("readonly"), "1", "%s must not be forced readonly" % field_name)
                self.assertNotEqual(node.get("column_invisible"), "1", "%s must stay visible" % field_name)

    def test_only_view_makes_margin_fields_readonly(self):
        for field_name, nodes in self._order_form_margin_nodes(self.only_view_user).items():
            for node in nodes:
                self.assertEqual(node.get("readonly"), "1", "%s must be readonly for view-only users" % field_name)
                self.assertNotEqual(node.get("column_invisible"), "1", "%s must stay visible" % field_name)

    def test_only_sale_price_hides_margin_fields(self):
        nodes_by_field = self._order_form_margin_nodes(self.only_sale_price_user)
        for field_name, nodes in nodes_by_field.items():
            for node in nodes:
                self.assertEqual(node.get("invisible"), "1", "%s must not be shown" % field_name)
        # purchase_price is a column of its own: column_invisible drops it.
        # margin and margin_percent sit inside the price_unit column, where the
        # web client ignores column_invisible on children and only invisible counts
        for node in nodes_by_field["purchase_price"]:
            self.assertEqual(node.get("column_invisible"), "1")

    def test_view_cache_does_not_leak_between_groups(self):
        """The arch is cached per view: a restricted user must not get the one
        built for a salesman, nor the other way around"""
        self._order_form_margin_nodes(self.salesman)
        restricted = self._order_form_margin_nodes(self.only_sale_price_user)
        self.assertEqual(restricted["margin"][0].get("invisible"), "1")
        plain = self._order_form_margin_nodes(self.salesman)
        self.assertNotEqual(plain["margin"][0].get("invisible"), "1")

    def _extra_total_labels(self, order, user):
        return [line["label"] for group in order.with_user(user).extra_total_fields for line in group.get("lines", [])]

    def test_only_sale_price_hides_order_total_margin(self):
        """In 20 sale_margin shows the order margin as a line of the extra totals
        widget, not as a block of the form view"""
        product = self.env["product.product"].create(
            {"name": "PSSM product", "list_price": 100.0, "standard_price": 40.0}
        )
        partner = self.env["res.partner"].create({"name": "PSSM customer"})
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": 1, "price_unit": 100.0, "discount": 10.0})
                ],
            }
        )
        self.assertTrue(order.margin)
        salesman_labels = self._extra_total_labels(order, self.salesman)
        self.assertTrue(any(label.startswith("Margin") for label in salesman_labels), salesman_labels)

        restricted_labels = self._extra_total_labels(order, self.only_sale_price_user)
        self.assertFalse(any(label.startswith("Margin") for label in restricted_labels), restricted_labels)
        # only the margin line goes away, the other extra totals stay
        self.assertEqual(restricted_labels, [label for label in salesman_labels if not label.startswith("Margin")])

    def test_line_view_cache_key_depends_on_groups(self):
        """The cache key this module adds on sale.order.line must split the
        users of each price security group"""
        line = self.env["sale.order.line"]
        keys = {
            user.login: line.with_user(user)._get_view_cache_key(False, "list")
            for user in (self.salesman, self.only_view_user, self.only_sale_price_user)
        }
        self.assertEqual(len(set(keys.values())), 3, keys)
