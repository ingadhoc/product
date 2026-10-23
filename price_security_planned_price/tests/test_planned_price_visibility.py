from lxml import etree
from odoo.tests import TransactionCase, new_test_user, tagged

# the fields product_planned_price adds to the product form, which this module
# locks for users that may only look at prices
PLANNED_PRICE_FIELDS = (
    "list_price_type",
    "computed_list_price_manual",
    "other_currency_list_price",
    "other_currency_id",
    "sale_margin",
    "sale_surcharge",
)
PRODUCT_MODELS = ("product.template", "product.product")


@tagged("post_install", "-at_install")
class TestPlannedPriceVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_groups = "base.group_user,sales_team.group_sale_manager"
        cls.plain_user = new_test_user(cls.env, login="psp_plain", groups=base_groups)
        cls.only_view_user = new_test_user(
            cls.env,
            login="psp_only_view",
            groups=base_groups + ",price_security.group_only_view",
        )
        # group_only_view_sale_price implies group_only_view, so this user gets both behaviours
        cls.only_sale_price_user = new_test_user(
            cls.env,
            login="psp_only_sale_price",
            groups=base_groups + ",price_security.group_only_view_sale_price",
        )

    def _form_arch(self, model, user):
        arch = self.env[model].with_user(user).get_view(view_type="form")["arch"]
        return etree.fromstring(arch)

    def _assert_readonly(self, arch, expected, model):
        for field_name in PLANNED_PRICE_FIELDS:
            nodes = arch.xpath("//field[@name='%s']" % field_name)
            self.assertTrue(nodes, "%s is expected on the %s form" % (field_name, model))
            for node in nodes:
                self.assertEqual(
                    node.get("readonly"),
                    expected,
                    "wrong readonly on %s of the %s form" % (field_name, model),
                )

    def _planned_price_group(self, arch, model):
        nodes = arch.xpath("//group[@name='planned_price']")
        self.assertTrue(nodes, "the planned price group is expected on the %s form" % model)
        return nodes

    def test_plain_user_keeps_the_planned_price_fields_editable(self):
        for model in PRODUCT_MODELS:
            with self.subTest(model=model):
                arch = self._form_arch(model, self.plain_user)
                self._assert_readonly(arch, None, model)
                for node in self._planned_price_group(arch, model):
                    self.assertIsNone(node.get("invisible"))

    def test_only_view_locks_the_planned_price_fields(self):
        for model in PRODUCT_MODELS:
            with self.subTest(model=model):
                arch = self._form_arch(model, self.only_view_user)
                self._assert_readonly(arch, "1", model)

    def test_only_view_keeps_the_planned_price_group_visible(self):
        """Seeing the sale price is a stricter group: only_view still shows the block"""
        for model in PRODUCT_MODELS:
            with self.subTest(model=model):
                arch = self._form_arch(model, self.only_view_user)
                for node in self._planned_price_group(arch, model):
                    self.assertIsNone(node.get("invisible"))

    def test_only_sale_price_hides_the_planned_price_group(self):
        for model in PRODUCT_MODELS:
            with self.subTest(model=model):
                arch = self._form_arch(model, self.only_sale_price_user)
                # the implied group still locks the fields
                self._assert_readonly(arch, "1", model)
                for node in self._planned_price_group(arch, model):
                    self.assertEqual(node.get("invisible"), "1")
