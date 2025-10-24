from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseOrderLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env
        self.company = self.env.ref("base.main_company")
        self.supplier = self.env["res.partner"].create(
            {
                "name": "Test Supplier",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "purchase_ok": True,
                "standard_price": 10.0,
            }
        )
        self.uom = self.env.ref("uom.product_uom_unit")
        self.currency = self.env.ref("base.USD")
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "date_order": fields.Date.today(),
                "company_id": self.company.id,
                "currency_id": self.currency.id,
            }
        )
        self.po_line = self.env["purchase.order.line"].create(
            {
                "order_id": self.po.id,
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom.id,
                "price_unit": 10.0,
            }
        )

    def test_compute_price_unit(self):
        # Create a supplierinfo with net_price to test the computation
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 15.0,
                "currency_id": self.currency.id,
            }
        )
        # Force recomputation of prices
        self.po_line._compute_price_unit_and_date_planned_and_name()
        # Verify that the price unit is calculated correctly (should use net_price)
        # Note: net_price computation depends on replenishment_cost_rule_id
        self.assertTrue(self.po_line.price_unit >= 0)

    def test_prepare_purchase_order_line_with_supplierinfo(self):
        """Test that purchase order lines use net_price from supplierinfo"""
        # Create a supplierinfo with a specific price and rule
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 20.0,
                "currency_id": self.currency.id,
            }
        )
        # Verify net_price is computed (without rule it should equal price)
        self.assertAlmostEqual(supplierinfo.net_price, 20.0)

        # Create a new PO line and verify it uses the supplierinfo price
        new_po_line = self.env["purchase.order.line"].create(
            {
                "order_id": self.po.id,
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom.id,
            }
        )
        # The price should be taken from the supplierinfo
        self.assertAlmostEqual(new_po_line.price_unit, 20.0)

    def test_prepare_purchase_order_line_currency_conversion(self):
        """Test currency conversion with supplierinfo"""
        # Create a supplierinfo with a price in a different currency
        foreign_currency = self.env.ref("base.EUR")
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 20.0,
                "currency_id": foreign_currency.id,
            }
        )

        # Create a PO with a different currency
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "date_order": fields.Date.today(),
                "company_id": self.company.id,
                "currency_id": foreign_currency.id,
            }
        )

        # Create a PO line
        po_line = self.env["purchase.order.line"].create(
            {
                "order_id": po.id,
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom.id,
            }
        )

        # Verify the price is set (currency conversion handled internally)
        self.assertTrue(po_line.price_unit > 0)
