from odoo.tests.common import TransactionCase
from odoo import fields
class TestPurchaseOrderLine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.env = self.env
        self.company = self.env.ref('base.main_company')
        self.supplier = self.env['res.partner'].create({
            'name': 'Test Supplier',
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'purchase_ok': True,
            'standard_price': 10.0,
        })
        self.uom = self.env.ref('uom.product_uom_unit')
        self.currency = self.env.ref('base.USD')
        self.po = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'date_order': fields.Date.today(),
            'company_id': self.company.id,
            'currency_id': self.currency.id,
        })
        self.po_line = self.env['purchase.order.line'].create({
            'order_id': self.po.id,
            'product_id': self.product.id,
            'product_qty': 1.0,
            'product_uom': self.uom.id,
            'price_unit': 10.0,
        })

    def test_compute_price_unit(self):
        # Forzamos la computación de precios
        self.po_line._compute_price_unit_and_date_planned_and_name()
        # Verifica que el precio unitario se calcule correctamente
        self.assertAlmostEqual(self.po_line.price_unit, 10.0)

    def test_prepare_purchase_order_line(self):
        # Simulamos un proveedor con un nuevo precio
        supplier = self.env['product.supplierinfo'].create({
            'partner_id': self.supplier.id,
            'product_id': self.product.id,
            'price': 20.0,
            'currency_id': self.currency.id,
        })
        # Preparamos la línea de pedido
        vals = self.po_line._prepare_purchase_order_line(
            self.product,
            1.0,
            self.uom,
            self.company,
            supplier,
            self.po
        )
        # Verifica que el precio unitario se ajuste correctamente
        self.assertAlmostEqual(vals['price_unit'], 20.0)

    def test_prepare_purchase_order_line_currency_conversion(self):
        # Simulamos un proveedor con un precio en una moneda diferente
        foreign_currency = self.env.ref('base.EUR')
        supplier = self.env['product.supplierinfo'].create({
            'partner_id': self.supplier.id,
            'product_id': self.product.id,
            'price': 20.0,
            'currency_id': foreign_currency.id,
        })
        # Simulamos un pedido con una moneda diferente
        po = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'date_order': fields.Date.today(),
            'company_id': self.company.id,
            'currency_id': foreign_currency.id,
        })
        # Preparamos la línea de pedido
        vals = self.po_line._prepare_purchase_order_line(
            self.product,
            1.0,
            self.uom,
            self.company,
            supplier,
            po
        )
        # Verifica la conversión de la moneda
        expected_price = supplier.currency_id._convert(
            20.0,
            po.currency_id,
            po.company_id,
            po.date_order or fields.Date.today()
        )
        self.assertAlmostEqual(vals['price_unit'], expected_price)
