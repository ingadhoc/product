##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged


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
