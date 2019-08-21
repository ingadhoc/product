##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char(
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'product.default_code') or '/',
    )
