##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def get_product_uoms(self, product_uom, use=False):
        """
        if product has uoms configured, we use them
        if not, we choose all uoms from uom_id category (first the product uom)
        We send product uom so it can be send from sale or purchase
        """
        self.ensure_one()
        return product_uom + self.env['uom.uom'].search([
            ('category_id', '=', product_uom.category_id.id),
            ('id', '!=', product_uom.id)])
