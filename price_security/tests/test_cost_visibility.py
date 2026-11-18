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

    def _get_arch(self, model, view_xmlid, view_type):
        view = self.env.ref(view_xmlid)
        arch = self.env[model].with_user(self.restricted_user).get_view(view.id, view_type)["arch"]
        return etree.fromstring(arch)

    def _assert_fields_dropped(self, arch, model, field_names):
        """A field the user can not read has to leave the arch: the web client
        resolves every node against the fields the view returns"""
        for field_name in field_names:
            if field_name not in self.env[model]._fields:
                continue
            self.assertFalse(
                arch.xpath("//field[@name='%s']" % field_name),
                "%s must not be left on the view of a user that only sees the sale price" % field_name,
            )

    def test_stock_report_drops_cost_columns(self):
        """The stock report (Inventory > Reporting > Stock) must not leak the
        valuation columns that stock_account adds to it
        """
        arch = self._get_arch("product.product", "stock.product_product_stock_tree", "list")
        self._assert_fields_dropped(
            arch,
            "product.product",
            ("avg_cost", "total_value", "avg_cost_in_currency", "total_value_in_currency"),
        )

    def test_product_list_drops_the_cost(self):
        arch = self._get_arch("product.template", "product.product_template_tree_view", "list")
        self._assert_fields_dropped(arch, "product.template", ("standard_price",))

    def test_product_form_drops_the_cost(self):
        arch = self._get_arch("product.template", "product.product_template_form_view", "form")
        self._assert_fields_dropped(arch, "product.template", ("standard_price",))
        self.assertFalse(arch.xpath("//label[@for='standard_price']"))

    def test_quant_list_drops_the_value(self):
        arch = self._get_arch("stock.quant", "stock.view_stock_quant_tree_editable", "list")
        self._assert_fields_dropped(arch, "stock.quant", ("value", "secondary_value"))

    def test_lot_form_drops_the_cost(self):
        arch = self._get_arch("stock.lot", "stock.view_production_lot_form", "form")
        self._assert_fields_dropped(arch, "stock.lot", ("total_value", "avg_cost", "standard_price"))

    def test_value_adjustments_drops_the_value(self):
        """Inventory > Reporting > Value Adjustments, the report of the ticket"""
        arch = self._get_arch("product.value", "stock_account.product_value_form_view", "form")
        self._assert_fields_dropped(arch, "product.value", ("value", "current_value"))

    def test_unrestricted_user_still_sees_cost(self):
        arch = etree.fromstring(
            self.env["product.product"].get_view(self.env.ref("stock.product_product_stock_tree").id, "list")["arch"]
        )
        self.assertTrue(arch.xpath("//field[@name='total_value']"))


@tagged("post_install", "-at_install")
class TestViewsAreConsistent(TransactionCase):
    """The regression this guards: dropping a field from fields_get without
    dropping it from the arch makes the web client crash with "field is
    undefined" as soon as any view still declares it."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restricted_user = new_test_user(
            cls.env,
            login="price_security_view_reader",
            groups="base.group_user,sales_team.group_sale_salesman_all_leads,"
            "stock.group_stock_manager,price_security.group_only_view_sale_price",
        )

    def _node_model(self, node, root_model, models):
        """Model a field node belongs to, walking up the x2many chain"""
        chain = []
        parent = node.getparent()
        while parent is not None:
            if parent.tag == "field":
                chain.append(parent.get("name"))
            parent = parent.getparent()
        model = root_model
        for field_name in reversed(chain):
            relation = models.get(model, {}).get("fields", {}).get(field_name, {}).get("relation")
            if not relation:
                return None
            model = relation
        return model

    def test_no_view_declares_a_field_the_user_can_not_read(self):
        models = [
            model
            for model in (
                "product.template",
                "product.product",
                "sale.order",
                "sale.order.line",
                "stock.quant",
                "stock.lot",
                "stock.move",
                "product.value",
            )
            if model in self.env
        ]
        views = self.env["ir.ui.view"].search(
            [
                ("model", "in", models),
                ("mode", "=", "primary"),
                ("type", "in", ["form", "list", "kanban", "search", "pivot", "graph"]),
            ]
        )
        problems = []
        for view in views:
            result = self.env[view.model].with_user(self.restricted_user).get_views([(view.id, view.type)])
            for arch in (etree.fromstring(v["arch"]) for v in result["views"].values()):
                for node in arch.iter("field"):
                    model = self._node_model(node, view.model, result["models"])
                    if model is None:
                        continue
                    fields = result["models"].get(model, {}).get("fields", {})
                    if node.get("name") not in fields:
                        problems.append("%s.%s in %s" % (model, node.get("name"), view.xml_id or view.id))
        self.assertFalse(sorted(set(problems)))
