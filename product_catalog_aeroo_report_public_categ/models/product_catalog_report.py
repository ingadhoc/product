##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductCatalogReport(models.Model):
    _inherit = "product.product_catalog_report"

    category_type = fields.Selection(
        selection_add=[("public_category", "Public Category")], ondelete={"public_category": "set default"}
    )
    public_category_ids = fields.Many2many(
        "product.public.category",
        "product_catalog_report_categories_public",
        "product_catalog_report_id",
        "category_id",
        "Product Categories Public",
    )

    def _public_categories(self):
        """The public categories of the report, with their children if asked."""
        self.ensure_one()
        categories = self.public_category_ids
        if self.include_sub_categories and categories:
            categories = self.env["product.public.category"].search([("id", "child_of", categories.ids)])
        return categories

    def prepare_report(self):
        self = super().prepare_report()
        if self.category_type == "public_category":
            self = self.with_context(category_ids=self._public_categories().ids)
        return self

    def get_categories(self):
        # The parent resolves the categories out of category_ids, which holds
        # product categories and stays empty when the public ones are used.
        if self.category_type != "public_category":
            return super().get_categories()
        self.ensure_one()
        categories = self._public_categories()
        if not categories:
            return self.env["product.public.category"]
        return self.env["product.public.category"].search(
            [("id", "in", categories.ids)], order=self.categories_order or "id"
        )
