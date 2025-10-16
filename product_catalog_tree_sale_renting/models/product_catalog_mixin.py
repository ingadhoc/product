from odoo import models


class ProductCatalogMixin(models.AbstractModel):
    _inherit = "product.catalog.mixin"
    _description = "Product Catalog Mixin"

    def action_add_from_catalog(self):
        res = super().action_add_from_catalog()
        list_view_id = self.env.ref("product_catalog_tree.product_view_tree_catalog").id
        unique_views = {}
        for view_id, view_type in res.get("views", []):
            if view_type != "list" and view_type not in unique_views:
                unique_views[view_type] = (view_id, view_type)
        res["views"] = [(list_view_id, "list")] + list(unique_views.values())
        return res
