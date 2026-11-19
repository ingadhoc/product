from lxml import etree
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCatalogTreeStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor Supplier UoM"})
        cls.box = cls.env["uom.uom"].create(
            {
                "name": "Caja test",
                "relative_factor": 12,
                "relative_uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product = cls.env["product.product"].create({"name": "Bottle", "purchase_ok": True})
        cls.env.user.group_ids |= cls.env.ref("uom.group_uom")
        with Form(cls.env["product.supplierinfo"].with_context(visible_product_tmpl_id=False)) as seller:
            seller.partner_id = cls.vendor
            seller.product_tmpl_id = cls.product.product_tmpl_id
            seller.uom_id = cls.box

    def test_supplier_uom_is_the_unit_of_the_vendor_pricelist(self):
        """The catalog shows the unit of the vendor pricelist of the order."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase is not installed")

        order = self.env["purchase.order"].create({"partner_id": self.vendor.id})
        catalog_product = self.product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )
        self.assertEqual(catalog_product.product_catalog_supplier_uom, "Caja test")

    def test_supplier_uom_is_empty_without_a_purchase_order(self):
        """Outside a purchase order catalog the column has no value."""
        self.assertFalse(self.product.product_catalog_supplier_uom)

    def test_catalog_view_hides_the_columns_that_do_not_apply(self):
        """The columns that make no sense in the catalog are hidden."""
        view = self.env.ref("product_catalog_tree.product_view_tree_catalog")
        arch = self.env["product.product"].get_view(view_id=view.id)["arch"]
        currency = etree.XML(arch).xpath("//field[@name='currency_id']")
        self.assertTrue(currency)
        self.assertEqual(currency[0].get("column_invisible"), "1")
