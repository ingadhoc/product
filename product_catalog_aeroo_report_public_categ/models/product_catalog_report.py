##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class ProductCatalogReport(models.Model):
    _inherit = 'product.product_catalog_report'

    category_type = fields.Selection(
        selection_add=[('public_category', 'Public Category')],
    )
    public_category_ids = fields.Many2many(
        'product.public.category',
        'product_catalog_report_categories_public',
        'product_catalog_report_id',
        'category_id',
        'Product Categories Public',
    )

    @api.multi
    def prepare_report(self):
        self = super().prepare_report()
        if self.category_type == 'public_category':
            categories = self.public_category_ids
            if self.include_sub_categories and categories:
                categories = self.env['product.public.category'].search(
                    [('id', 'child_of', categories.ids)])
            self = self.with_context(category_ids=categories.ids)
        return self
