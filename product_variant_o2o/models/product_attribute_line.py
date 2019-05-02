from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductAttributeLine(models.Model):
    _inherit = 'product.attribute.line'

    @api.constrains('value_ids', 'product_tmpl_id')
    def _check_one_variant_per_product(self):
        products = self.filtered(
            lambda x: x.product_tmpl_id.one_variant_per_product and
            len(x.value_ids) > 1).mapped('product_tmpl_id')
        if products:
            raise ValidationError(_(
                "Only 1 value per attribute allowed on products: %s") % (
                    ', '.join(products.mapped('name'))
                ))
