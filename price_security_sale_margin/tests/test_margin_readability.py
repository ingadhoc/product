from lxml import etree
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestMarginReadability(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restricted_user = new_test_user(
            cls.env,
            login="price_security_margin_reader",
            groups="base.group_user,sales_team.group_sale_salesman_all_leads,"
            "price_security.group_only_view_sale_price",
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Restricted margin product", "list_price": 150.0, "standard_price": 100.0}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Margin reader customer"})

    def _as_user(self, model):
        return self.env[model].with_user(self.restricted_user)

    def _create_order(self):
        return (
            self.env["sale.order"]
            .with_user(self.restricted_user)
            .create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [(0, 0, {"product_id": self.product.id, "product_uom_qty": 2})],
                }
            )
        )

    def test_restricted_user_can_still_work_with_sale_orders(self):
        """The margin is precomputed: denying the field access would break this"""
        order = self._create_order()
        order.order_line.product_uom_qty = 5
        order.action_confirm()
        self.assertEqual(order.state, "sale")
        sudo_line = self.env["sale.order.line"].browse(order.order_line.id)
        self.assertEqual(sudo_line.purchase_price, 100.0)

    def test_the_order_list_does_not_trip_on_the_margin(self):
        """Reading any order field prefetches the lines, the margin included"""
        self._create_order()
        records = self._as_user("sale.order").web_search_read([], {"name": {}, "expected_date": {}})["records"]
        self.assertTrue(records)

    def test_fields_get_does_not_offer_the_margin(self):
        fields = self._as_user("sale.order.line").fields_get()
        for field_name in ("purchase_price", "margin", "margin_percent"):
            self.assertNotIn(field_name, fields)

    def test_reading_the_margin_returns_nothing(self):
        line = self._create_order().order_line
        values = self._as_user("sale.order.line").browse(line.id).read(["margin"])
        self.assertFalse(values[0]["margin"])

    def test_grouping_by_the_margin_is_denied(self):
        with self.assertRaises(AccessError):
            self._as_user("sale.order.line")._read_group([], [], ["margin:sum"])

    def test_searching_by_the_margin_is_denied(self):
        with self.assertRaises(AccessError):
            self._as_user("sale.order.line").search_count([("margin", ">", 0)])

    def test_ordering_by_the_margin_is_denied(self):
        with self.assertRaises(AccessError):
            self._as_user("sale.order.line").search([], order="margin desc", limit=1)

    def test_margin_is_out_of_the_order_form(self):
        arch = etree.fromstring(self._as_user("sale.order").get_view(False, "form")["arch"])
        for field_name in ("purchase_price", "margin", "margin_percent"):
            self.assertFalse(arch.xpath("//field[@name='%s']" % field_name))

    def test_unrestricted_user_still_reads_the_margin(self):
        line = self._create_order().order_line
        self.assertTrue(self.env["sale.order.line"].browse(line.id).read(["margin"])[0]["margin"])
        arch = etree.fromstring(self.env["sale.order"].get_view(False, "form")["arch"])
        self.assertTrue(arch.xpath("//field[@name='margin']"))
