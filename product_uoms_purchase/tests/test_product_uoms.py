from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductUoms(TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplier = self.env["res.partner"].create({"name": "Test Supplier"})
        self.main_uom = self.env.ref("uom.product_uom_unit")
        self.secondary_uom = self.env.ref("uom.product_uom_dozen")
        self.product_template = self.env["product.template"].create(
            {
                "name": "Test Product With Purchase Secondary UoM",
                "uom_id": self.main_uom.id,
                "uom_po_id": self.main_uom.id,
                "purchase_ok": True,
            }
        )
        self.secondary_product_uom = self.env["product.uoms"].create(
            {
                "product_tmpl_id": self.product_template.id,
                "uom_id": self.secondary_uom.id,
                "purchase_ok": True,
            }
        )
        self.purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "date_order": fields.Date.today(),
            }
        )
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product_template.name,
                "product_id": self.product_template.product_variant_id.id,
                "product_qty": 1.0,
                "product_uom": self.secondary_uom.id,
                "price_unit": 100.0,
                "date_planned": fields.Datetime.now(),
            }
        )

    def test_cannot_unlink_secondary_uom_used_in_purchase_order(self):
        with self.assertRaises(ValidationError):
            self.secondary_product_uom.unlink()
