##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.tools import create_index


class ProductProduct(models.Model):
    _inherit = "product.product"
    _order = "default_code, name, id"

    def init(self):
        super().init()
        create_index(
            self.env.cr,
            indexname="is_favorite_idx",
            tablename="product_product",
            expressions=["is_favorite"],
            where="is_favorite IS TRUE",
        )

    active = fields.Boolean(tracking=True)
    pricelist_price = fields.Float(compute="_compute_product_pricelist_price", digits="Product Price")
    is_favorite = fields.Boolean(related="product_tmpl_id.is_favorite", readonly=True, store=True)

    @api.depends_context("pricelist", "quantity", "uom", "date", "no_variant_attributes_price_extra")
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()
