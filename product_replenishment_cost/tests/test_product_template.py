from odoo.tests.common import TransactionCase
from datetime import datetime
from unittest.mock import patch

class TestProductTemplate(TransactionCase):

    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.ProductTemplate = self.env['product.template']
        self.ResCurrency = self.env['res.currency']
        self.ProductSupplierInfo = self.env['product.supplierinfo']
        self.ResPartner = self.env['res.partner']
        self.ReplenishmentCostRule = self.env['product.replenishment_cost.rule']

        self.currency1 = self.ResCurrency.create({
            'name': 'CUR1',
            'symbol': '**C1**',
            'rate': 1.0
        })
        self.currency2 = self.ResCurrency.create({
            'name': 'CUR2',
            'symbol': '**C2**',
            'rate': 1.5
        })

        self.replenishment_cost_rule = self.ReplenishmentCostRule.create({
            'name': 'Test Rule',
            'item_ids': [(0, 0, {'sequence': 1, 'percentage_amount': 10.0})]
        })

        self.supplier = self.ResPartner.create({
            'name': 'Test Supplier',
        })

        self.product_template = self.ProductTemplate.create({
            'name': 'Test Product',
            'standard_price': 100.0,
            'replenishment_base_cost': 80.0,
            'replenishment_base_cost_currency_id': self.currency1.id,
            'replenishment_cost_type': 'manual',
            'replenishment_cost_rule_id': self.replenishment_cost_rule.id,
        })

        def test_compute_replenishment_cost(self):
            self.product_template._compute_replenishment_cost()
            self.assertEqual(self.product_template.replenishment_cost, 80.0)
            self.assertEqual(self.product_template.replenishment_base_cost_on_currency, 80.0)

        def test_compute_supplier_data(self):
            self.supplier_info1 = self.ProductSupplierInfo.create({
                'product_tmpl_id': self.product_template.id,
                'partner_id': self.supplier.id,
                'currency_id': self.currency1.id,
                'net_price': 120.0,
                'last_date_price_updated': '2024-01-01',
            })
            self.supplier_info2 = self.ProductSupplierInfo.create({
                'product_tmpl_id': self.product_template.id,
                'partner_id': self.supplier.id,
                'currency_id': self.currency2.id,
                'net_price': 100.0,
                'last_date_price_updated': '2024-08-01',
            })

            self.product_template.replenishment_cost_type = 'last_supplier_price'
            self.product_template._compute_supplier_data()

            self.assertEqual(self.product_template.supplier_price, 100.0)
            self.assertEqual(self.product_template.supplier_currency_id, self.currency2)

        def test_replenishment_cost_last_update(self):
            initial_update_time = self.product_template.replenishment_cost_last_update

            self.product_template.write({'replenishment_base_cost': 90.0})
            self.product_template._compute_replenishment_cost()

            new_update_time = self.product_template.replenishment_cost_last_update

            self.assertNotEqual(new_update_time, initial_update_time)
            self.assertGreater(new_update_time, initial_update_time)

class TestUpdateCostFromReplenishmentCost(TransactionCase):

    def setUp(self):
        super(TestUpdateCostFromReplenishmentCost, self).setUp()
        self.ProductTemplate = self.env['product.template']
        self.product_template = self.ProductTemplate.create({
            'name': 'Test Product',
            'standard_price': 100.0,
            'replenishment_base_cost': 80.0,
            'replenishment_base_cost_currency_id': self.env.ref('base.USD').id,
            'replenishment_cost_type': 'manual',
            'currency_id': self.env.ref('base.EUR').id,
        })

    def test_update_cost_from_replenishment_cost(self):
        product = self.env['product.product'].create({
            'product_tmpl_id': self.product_template.id,
            'standard_price': 100.0,
            'currency_id': self.env.ref('base.EUR').id,
        })

        self.product_template._update_cost_from_replenishment_cost()

        self.assertEqual(product.standard_price, 80.0)
