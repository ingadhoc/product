##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code(
            'product.default_code') or '/'

    default_code = fields.Char(
        default=_get_default_code,
    )
