from odoo import models


class ProductCatalogMixin(models.AbstractModel):
    _inherit = "product.catalog.mixin"
    _description = "Product Catalog Mixin"

    def action_add_from_catalog(self):
        action = super().action_add_from_catalog()
        tree_view_id = self.env.ref("product_catalog_tree.product_view_tree_catalog").id
        search_view_id = self.env.ref("product.product_search_form_view").id
        action["views"] = [(tree_view_id, "list")] + action["views"]
        action["search_view_id"] = (search_view_id, "search")
        # add warehouse location filter if order has warehouse
        context = action.get("context", {})
        if "order_id" in context and self._name == "sale.order":
            if self._fields.get("warehouse_id") and self.warehouse_id:
                action["context"]["search_default_location_id"] = self.warehouse_id.lot_stock_id.id
        return action
