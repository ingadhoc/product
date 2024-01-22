##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    active = fields.Boolean(tracking=True)
    pricelist_price = fields.Float(compute='_compute_product_pricelist_price', digits='Product Price')

    @api.depends_context('pricelist', 'quantity', 'uom', 'date', 'no_variant_attributes_price_extra')
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()
