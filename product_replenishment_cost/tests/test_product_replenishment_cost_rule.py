from odoo.tests.common import TransactionCase

class TestProductReplenishmentCostRule(TransactionCase):

    def setUp(self):
        super(TestProductReplenishmentCostRule, self).setUp()
        self.product_replenishment_cost_rule = self.env['product.replenishment_cost.rule'].create({
            'name': 'Test Rule',
        })

        self.product = self.env['product.template'].create({
            'name': 'Test Product',
            'replenishment_cost_rule_id': self.product_replenishment_cost_rule.id
        })

        self.item1 = self.env['product.replenishment_cost.rule.item'].create({
            'name': 'Item 1',
            'percentage_amount': 10.0,
            'fixed_amount': 5.0,
            'replenishment_cost_rule_id': self.product_replenishment_cost_rule.id,
        })

    def test_compute_description(self):
        self.product_replenishment_cost_rule.item_ids = [(6, 0, [self.item1.id])]
        self.product_replenishment_cost_rule._compute_description()

        expected_description = "Test Rule: Item 1 10.0 + 5.0"
        self.assertEqual(self.product_replenishment_cost_rule.description, expected_description)

    def test_compute_rule_inverse(self):
        self.product_replenishment_cost_rule.item_ids = [(6, 0, [self.item1.id])]
        final_cost = 115

        # Calcula el costo original utilizando el método inverso
        original_cost = self.product_replenishment_cost_rule.compute_rule_inverse(final_cost)
        expected_original_cost = 100.0
        self.assertAlmostEqual(original_cost, expected_original_cost, places=2)

    def test_compute_rule(self):
        self.product_replenishment_cost_rule.item_ids = [(6, 0, [self.item1.id])]
        initial_cost = 100.0
        final_cost = self.product_replenishment_cost_rule.compute_rule(initial_cost, self.product)
        self.assertAlmostEqual(final_cost, 115, places=2)  # Ajusta el valor esperado

    def test_get_eval_context(self):
        context = self.product_replenishment_cost_rule._get_eval_context(self.product)
        self.assertIn('env', context)
        self.assertIn('model', context)
        self.assertIn('UserError', context)
        self.assertIn('product', context)
        self.assertEqual(context['product'], self.product)
