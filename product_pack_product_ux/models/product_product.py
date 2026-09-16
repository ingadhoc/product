##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends_context("product_catalog_order_model", "product_catalog_order_id", "order_id")
    def _compute_product_pricelist_price(self):
        records = self.with_context(**self.env["product.template"]._get_pack_pricelist_price_context())
        super(ProductProduct, records)._compute_product_pricelist_price()
        for product, record in zip(self, records):
            product.pricelist_price = record.pricelist_price
