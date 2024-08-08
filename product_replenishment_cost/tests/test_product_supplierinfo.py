from odoo.tests.common import TransactionCase

class TestProductSupplierinfo(TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfo, self).setUp()
        # Crea los datos necesarios para las pruebas
        self.product_template = self.env['product.template'].create({
            'name': 'Test Product',
            'list_price': 100.0,
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Test Supplier Partner',
        })

        self.replenishment_cost_rule = self.env['product.replenishment_cost.rule'].create({
            'name': 'Test Rule',
            'item_ids': [(0, 0, {
                'name': 'Test Item',
                'sequence': 1,
                'percentage_amount': 10.0,
                'fixed_amount': 5.0,
            })]
        })

        self.supplierinfo = self.env['product.supplierinfo'].create({
            'partner_id': self.partner.id,
            'product_tmpl_id': self.product_template.id,
            'price': 100.0,
            'currency_id': self.env.ref('base.USD').id,
            'replenishment_cost_rule_id': self.replenishment_cost_rule.id,
        })

    def test_last_date_price_updated(self):
        """ Test that last_date_price_updated is updated correctly """
        self.supplierinfo._compute_last_date_price_updated()
        self.assertIsNotNone(self.supplierinfo.last_date_price_updated, "Last date price updated should not be None")

    def test_compute_rule_inverse(self):
        # Calcula el costo esperado aplicando la regla en orden inverso
        initial_cost = 100.0  # El costo base que queremos ajustar
        fixed_amount = 5.0
        percentage_amount = 10.0
        # Aplica el ajuste inverso
        expected_cost = (initial_cost - fixed_amount) / (1.0 + percentage_amount / 100.0)
        
        # Obtén el resultado del método `compute_rule_inverse`
        result = self.replenishment_cost_rule.compute_rule_inverse(initial_cost)
        
        # Verifica si el resultado es el esperado
        self.assertAlmostEqual(result, expected_cost, places=2)
