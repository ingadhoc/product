from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductUoms(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Customer"})
        self.main_uom = self.env.ref("uom.product_uom_unit")
        self.secondary_uom = self.env.ref("uom.product_uom_dozen")
        self.product_template = self.env["product.template"].create(
            {
                "name": "Test Product With Secondary UoM",
                "uom_id": self.main_uom.id,
                "uom_po_id": self.main_uom.id,
                "list_price": 100.0,
            }
        )
        self.secondary_product_uom = self.env["product.uoms"].create(
            {
                "product_tmpl_id": self.product_template.id,
                "uom_id": self.secondary_uom.id,
                "sale_ok": True,
            }
        )
        self.sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": self.product_template.name,
                "product_id": self.product_template.product_variant_id.id,
                "product_uom": self.secondary_uom.id,
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
            }
        )

    def test_cannot_unlink_secondary_uom_used_in_sale_order(self):
        with self.assertRaises(ValidationError):
            self.secondary_product_uom.unlink()
