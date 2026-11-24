##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user


class TestProductManagementGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Managed product"})
        # Native product managers are still blocked without the module group
        cls.user_native = new_test_user(
            cls.env, login="pmg_native", groups="base.group_user,product.group_product_manager"
        )
        # The module group alone is enough to manage products
        cls.user_managed = new_test_user(
            cls.env,
            login="pmg_managed",
            groups="base.group_user,product_management_group.group_products_management",
        )

    def test_without_group_cannot_manage_products(self):
        env = self.env(user=self.user_native)
        product = self.product.with_env(env)
        self.assertEqual(product.name, "Managed product")
        self.assertFalse(env["product.template"].has_access("create"))
        with self.assertRaisesRegex(AccessError, "Products Management"):
            env["product.template"].create({"name": "Blocked"})
        with self.assertRaises(AccessError):
            env["product.product"].create({"name": "Blocked"})
        with self.assertRaises(AccessError):
            product.write({"name": "Changed"})
        with self.assertRaises(AccessError):
            product.product_tmpl_id.write({"name": "Changed"})
        with self.assertRaises(AccessError):
            product.unlink()

    def test_with_group_can_manage_products(self):
        env = self.env(user=self.user_managed)
        self.assertTrue(env["product.template"].has_access("create"))
        template = env["product.template"].create({"name": "Allowed"})
        variant = env["product.product"].create({"name": "Allowed variant"})
        template.write({"name": "Allowed changed"})
        self.product.with_env(env).write({"name": "Changed"})
        self.assertEqual(self.product.name, "Changed")
        variant.unlink()
        template.unlink()
        self.assertFalse(template.exists())
