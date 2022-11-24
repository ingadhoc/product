##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    active = fields.Boolean(tracking=True)
    sellers_product_code = fields.Char(
        'Vendor Product Code',
        related='seller_ids.product_code',
    )
    warranty = fields.Float()
    pricelist_price = fields.Float(compute='_compute_product_pricelist_price', digits='Product Price')
    pricelist_id = fields.Many2one('product.pricelist', store=False,)

    @api.depends_context('pricelist', 'quantity', 'uom', 'date', 'no_variant_attributes_price_extra')
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()
