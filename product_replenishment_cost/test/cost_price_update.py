
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import odoo.tests.common as common


class CostPriceUpdate(common.TransactionCase):

    def setUp(self):
        super().setUp()
        obj_product = self.env['product.product']

        # Create a wine A product
        self.product_product_a = obj_product.create({
            'categ_id':  self.env.ref('product.product_category_1').id,
            'name': 'Wine A01',
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'uom_po_id': self.env.ref('product.product_uom_unit').id,
            'company_id': 1,
            'standard_price': 50.0,
            'list_price': 75.0,
        })

    # Test the prices are updated correctly
    def test_prices_update_correclty(self):
        # 01 The standard_price has not been recorded correctly
        self.assertEquals(self.product_product_a.standard_price, 50.0)
        # "01 The replenishment_cost has not been recorded correctly
        self.assertEquals(self.product_product_a.replenishment_cost, 0.0)

    # Modify product A set new prices
    def test_prices_new_prices(self):
        self.product_product_a.write({'standard_price': 70})
        # 02 The standard_price has not been recorded correctly
        self.assertEquals(self.product_product_a.standard_price, 70.0)

    # Set replenishment cost
    def test_set_replenishment_Cost(self):
        product_tmpl = self.product_product_a.product_tmpl_id
        product_tmpl.write({'replenishment_base_cost': 100.0})
        # 03 The replenishment_base_cost has not been recorded correctly
        self.assertEquals(product_tmpl.replenishment_base_cost, 100.0)
        # 04 The replenishment_cost has not been recorded correctly
        self.assertEquals(product_tmpl.replenishment_cost, 100.0)

    # Run wizard named 'Update Accounting Cost from Replenishment Cost'
    def test_run_wizard(self):
        product_template = self.product_product_a.product_tmpl_id
        wizard = self.env[
            'product.update_from_replenishment_cost.wizard'].with_context(
            {'active_model': 'product.template',
                'active_id': product_template.id,
                'active_ids': [product_template.id]}).create({})
        wizard.confirm()
        # 05 The standard_price has not been updated correctly
        self.assertEquals(product_template.standard_price, 100.0)
