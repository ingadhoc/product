from odoo import api
from odoo.tests import tagged

from .common import PurchaseUomsCommon


@tagged("post_install", "-at_install")
class TestPurchaseCatalog(PurchaseUomsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # the catalog checks the UoM feature on the superuser
        cls.env["res.users"].sudo().browse(api.SUPERUSER_ID).group_ids |= cls.env.ref("uom.group_uom")
        cls.product.standard_price = 2
        cls.other_vendor = cls.env["res.partner"].create({"name": "Vendor without pricelist"})

    def _catalog_data(self, partner):
        order = self.env["purchase.order"].create({"partner_id": partner.id})
        return order, order._get_product_catalog_product_data(self.product)

    def _uom_ids(self, data):
        return {uom["id"] for uom in data["availableUoms"]}

    def test_catalog_uoms_with_product_uom(self):
        _order, data = self._catalog_data(self.vendor)
        self.assertEqual(self._uom_ids(data), set((self.unit | self.pack | self.box).ids))

    def test_catalog_uoms_without_product_uom(self):
        self.product.use_product_uom = False
        _order, data = self._catalog_data(self.vendor)
        self.assertEqual(self._uom_ids(data), set((self.pack | self.box).ids))
        self.assertNotIn(self.dozen.id, self._uom_ids(data))

    def test_catalog_default_uom_is_allowed(self):
        """Without a pricelist for the order vendor the core proposes the product UoM:
        when it is not allowed, the catalog starts with a purchase packaging instead
        """
        self.product.use_product_uom = False
        _order, data = self._catalog_data(self.other_vendor)
        self.assertEqual(data["uomId"], self.pack.id)
        self.assertEqual(self._uom_ids(data), set((self.pack | self.box).ids))
        self.assertAlmostEqual(data["price"], 12)

    def test_catalog_default_uom_kept_when_allowed(self):
        _order, data = self._catalog_data(self.other_vendor)
        self.assertEqual(data["uomId"], self.unit.id)
        _order, data = self._catalog_data(self.vendor)
        self.assertEqual(data["uomId"], self.box.id)

    def test_catalog_line_uses_allowed_uom(self):
        self.product.use_product_uom = False
        order, data = self._catalog_data(self.other_vendor)
        order._update_order_line_info(
            product=self.product,
            quantity=1,
            uom=self.env["uom.uom"].browse(data["uomId"]),
            child_field="order_line",
        )
        self.assertEqual(order.order_line.uom_id, self.pack)
        self.assertIn(order.order_line.uom_id, order.order_line.allowed_uom_ids)
