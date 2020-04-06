##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code('product.default_code')

    default_code = fields.Char(
        required=True,
        default=_get_default_code,
    )

    @api.model
    def create(self, vals):
        if not vals.get('default_code', False) and vals.get('product_tmpl_id', False):
            product_tmpl = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            vals['default_code'] = product_tmpl.default_code or self.env['ir.sequence'].next_by_code(
                'product.default_code')
        return super().create(vals)
