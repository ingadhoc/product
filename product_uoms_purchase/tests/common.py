from odoo.tests import TransactionCase


class PurchaseUomsCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("uom.group_uom")
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.dozen = cls.env.ref("uom.product_uom_dozen")
        cls.pack = cls.env["uom.uom"].create({"name": "Pack 6", "relative_factor": 6, "relative_uom_id": cls.unit.id})
        cls.box = cls.env["uom.uom"].create({"name": "Box 12", "relative_factor": 12, "relative_uom_id": cls.unit.id})
        cls.vendor = cls.env["res.partner"].create({"name": "UoM Vendor"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product with purchase packagings",
                "uom_id": cls.unit.id,
                "uom_ids": [(6, 0, cls.dozen.ids)],
                "uom_po_ids": [(6, 0, cls.pack.ids)],
                "seller_ids": [(0, 0, {"partner_id": cls.vendor.id, "uom_id": cls.box.id, "price": 10})],
            }
        )

    def _new_line(self):
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor.id, "order_line": [(0, 0, {"product_id": self.product.id, "product_qty": 1})]}
        )
        return order.order_line
