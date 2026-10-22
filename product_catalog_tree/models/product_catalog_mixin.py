from odoo import models

# Child fields of the catalog lines on which the list knows how to write: the lines of sale and purchase
# orders, and of invoices
LIST_CATALOG_CHILD_FIELDS = ("order_line", "line_ids")


class ProductCatalogMixin(models.AbstractModel):
    _inherit = "product.catalog.mixin"
    _description = "Product Catalog Mixin"

    def action_add_from_catalog(self):
        action = super().action_add_from_catalog()
        if self.env.context.get("child_field") not in LIST_CATALOG_CHILD_FIELDS:
            # Quotation templates, bills of materials, manufacturing and repair orders keep their own catalog
            return action
        tree_view_id = self.env.ref("product_catalog_tree.product_view_tree_catalog").id
        action["views"] = [(tree_view_id, "list")] + action["views"]
        # add warehouse location filter if order has warehouse
        context = action.get("context", {})
        if "order_id" in context and self._name == "sale.order":
            if self._fields.get("warehouse_id") and self.warehouse_id:
                action["context"]["search_default_location_id"] = self.warehouse_id.lot_stock_id.id
        return action
