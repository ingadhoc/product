##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'product.default_code'),
    )
