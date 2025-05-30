from odoo import _, models


class ProductCatalogMixin(models.AbstractModel):
    _inherit = 'product.catalog.mixin'
    _description = 'Product Catalog Mixin'

    def action_add_from_catalog(self):
        action = super().action_add_from_catalog()
        if self._name == "sale.order" and self.is_rental_order:
            tree_view_id = self.env.ref('product_catalog_tree.product_view_tree_catalog').id
            action['views'] = [view for view in action['views'] if view != (tree_view_id, 'tree')]
        return action
