##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductProduct(models.Model):
<<<<<<< 13e2d2f1c2fb0d8925efc0d6a663966c20d7dd12
    _name = "product.product"
    _inherit = ["product.product", "product.search.mixin"]
||||||| 20a98de6f8dababd58d0de573b0e41da633d2dc3
    _inherit = "product.product"
    _order = "default_code, name, id"
=======
    _name = "product.product"
    _inherit = ["product.product", "product.search.mixin"]
    _order = "default_code, name, id"
>>>>>>> 2dd56d98370fcab6b829592dd1b7b8048841e3b5

    # the configured paths start at product.template
    _search_path_prefix = "product_tmpl_id."

    active = fields.Boolean(tracking=True)
    pricelist_price = fields.Float(compute="_compute_product_pricelist_price", digits="Product Price")

    @api.depends_context("pricelist", "quantity", "uom", "date", "no_variant_attributes_price_extra")
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()
<<<<<<< 13e2d2f1c2fb0d8925efc0d6a663966c20d7dd12

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        results = super().name_search(name, domain, operator, limit)
        return self._extend_name_search(results, name, domain, operator, limit)
||||||| 20a98de6f8dababd58d0de573b0e41da633d2dc3
=======

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        results = super().name_search(name, args, operator, limit)
        return self._extend_name_search(results, name, args, operator, limit)

    @api.model
    def _search_path(self, path):
        """A field of the variant itself is searched here, or it would match its sibling variants."""
        field = self._fields.get(path.split(".")[0])
        return path if field is not None and not field.inherited else "product_tmpl_id." + path

    @api.model
    def _search_resolved_exactly(self, results, term):
        products = self.browse([res[0] for res in results]).sudo()
        return any(term in (product.default_code, product.barcode) for product in products)
>>>>>>> 2dd56d98370fcab6b829592dd1b7b8048841e3b5
