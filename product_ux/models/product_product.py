##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "product.search.mixin"]

    # the configured paths start at product.template
    _search_path_prefix = "product_tmpl_id."

    active = fields.Boolean(tracking=True)
    pricelist_price = fields.Float(compute="_compute_product_pricelist_price", digits="Product Price")

    @api.depends_context("pricelist", "quantity", "uom", "date", "no_variant_attributes_price_extra")
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        results = super().name_search(name, domain, operator, limit)
        return self._extend_name_search(results, name, domain, operator, limit)
