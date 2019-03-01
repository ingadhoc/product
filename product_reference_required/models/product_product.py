##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code(
            'product.default_code') or '/'

    default_code = fields.Char(
        required=True,
        default=_get_default_code,
    )
