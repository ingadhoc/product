from odoo.tests import Form, tagged

from .common import PurchaseUomsCommon


@tagged("post_install", "-at_install")
class TestPurchaseUoms(PurchaseUomsCommon):
    def test_use_product_uom_enabled_by_default(self):
        self.assertTrue(self.product.use_product_uom)

    def test_allowed_uoms_with_product_uom(self):
        line = self._new_line()
        self.assertEqual(line.allowed_uom_ids, self.unit | self.pack | self.box)

    def test_allowed_uoms_without_product_uom(self):
        self.product.use_product_uom = False
        line = self._new_line()
        self.assertEqual(line.allowed_uom_ids, self.pack | self.box)

    def test_sale_packagings_not_allowed(self):
        line = self._new_line()
        self.assertNotIn(self.dozen, line.allowed_uom_ids)

    def test_allowed_uoms_follow_product_setting(self):
        line = self._new_line()
        self.product.use_product_uom = False
        self.assertNotIn(self.unit, line.allowed_uom_ids)

    def test_purchase_packagings_on_product_form(self):
        with Form(self.product.product_tmpl_id) as template:
            template.uom_po_ids.add(self.box)
        self.assertEqual(self.product.uom_po_ids, self.pack | self.box)
