##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from datetime import timedelta

from odoo import fields
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCatalogTreePurchase(TransactionCase):
    """The catalog of a purchase order opens on the list, which purchase replaces with its own kanban."""

    def test_the_list_opens_first_on_purchase_orders(self):
        list_view = self.env.ref("product_catalog_tree.product_view_tree_catalog")
        # the kanban of purchase_stock wins over the one of purchase when it is installed
        purchase_kanban = self.env.ref(
            "purchase_stock.product_view_kanban_catalog_purchase_only", raise_if_not_found=False
        ) or self.env.ref("purchase.product_view_kanban_catalog_purchase_only")
        vendor = self.env["res.partner"].create({"name": "Catalog list vendor"})
        order = self.env["purchase.order"].create({"partner_id": vendor.id})

        action = order.with_context(order_id=order.id, child_field="order_line").action_add_from_catalog()

        self.assertEqual(action["views"][0], (list_view.id, "list"))
        # purchase leaves two kanbans behind: only the purchase one is kept, and the form survives
        self.assertEqual([view_type for _view_id, view_type in action["views"]], ["list", "kanban", "form"])
        self.assertEqual(
            [view_id for view_id, view_type in action["views"] if view_type == "kanban"], [purchase_kanban.id]
        )


@tagged("post_install", "-at_install")
class TestProductCatalogSupplierUom(TransactionCase):
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
        order = self.env["purchase.order"].create({"partner_id": self.vendor.id})
        catalog_product = self.product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )
        self.assertEqual(catalog_product.product_catalog_supplier_uom, "Caja test")

    def test_supplier_uom_comes_from_the_pricelist_of_the_price(self):
        """An expired pricelist is skipped, as purchase does for the price of the catalog."""
        unit = self.env.ref("uom.product_uom_unit")
        self.product.seller_ids.date_end = fields.Date.today() - timedelta(days=1)
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "uom_id": unit.id,
            }
        )
        order = self.env["purchase.order"].create({"partner_id": self.vendor.id})
        catalog_product = self.product.with_context(
            product_catalog_order_model="purchase.order",
            order_id=order.id,
        )
        self.assertEqual(catalog_product.product_catalog_supplier_uom, unit.name)

    def test_supplier_uom_is_empty_without_a_purchase_order(self):
        """Outside a purchase order catalog the column has no value."""
        self.assertFalse(self.product.product_catalog_supplier_uom)
