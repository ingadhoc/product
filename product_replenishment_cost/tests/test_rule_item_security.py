from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, new_test_user


class TestRuleItemSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.internal_user = new_test_user(cls.env, login="rc_internal", groups="base.group_user")
        cls.manager = new_test_user(cls.env, login="rc_manager", groups="sales_team.group_sale_manager")
        cls.expr_manager = new_test_user(
            cls.env,
            login="rc_expr_manager",
            groups="sales_team.group_sale_manager,product_replenishment_cost.group_replenishment_rule_expr",
        )
        cls.rule = cls.env["product.replenishment_cost.rule"].create(
            {"name": "Security Rule", "item_ids": [(0, 0, {"name": "Freight", "percentage_amount": 10.0})]}
        )
        cls.item = cls.rule.item_ids

    def test_internal_user_cannot_edit_rule_items(self):
        """Rule items are edited by whoever edits the rule: an internal user only reads them."""
        with self.assertRaises(AccessError):
            self.item.with_user(self.internal_user).write({"percentage_amount": 20.0})
        with self.assertRaises(AccessError):
            self.env["product.replenishment_cost.rule.item"].with_user(self.internal_user).create(
                {"name": "Extra", "replenishment_cost_rule_id": self.rule.id}
            )

    def test_expression_needs_the_expression_group(self):
        """The expression runs as python code: setting it needs the expression group, not only the rule access."""
        self.item.with_user(self.manager).write({"percentage_amount": 20.0})
        self.assertEqual(self.item.percentage_amount, 20.0)
        with self.assertRaises(AccessError):
            self.item.with_user(self.manager).write({"expr": "1.0"})
        with self.assertRaises(AccessError):
            self.item.with_user(self.manager).write({"expr": False})
        with self.assertRaises(AccessError):
            self.env["product.replenishment_cost.rule.item"].with_user(self.manager).create(
                {"name": "Extra", "replenishment_cost_rule_id": self.rule.id, "expr": "1.0"}
            )
        self.item.with_user(self.expr_manager).write({"expr": "1.0"})
        self.assertEqual(self.item.expr, "1.0")

    def test_internal_user_still_gets_the_cost(self):
        """Restricting the edition does not hide the cost computed with an expression."""
        self.item.write({"expr": "5.0"})
        product = self.env["product.template"].create(
            {
                "name": "Security Product",
                "replenishment_cost_type": "manual",
                "replenishment_base_cost": 100.0,
                "replenishment_cost_rule_id": self.rule.id,
            }
        )
        self.assertAlmostEqual(product.with_user(self.internal_user).replenishment_cost, 115.0)
