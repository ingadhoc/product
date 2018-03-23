##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code('product.default_code')

    default_code = fields.Char(
        required=True,
        default=_get_default_code,
    )

    @api.model
    def create(self, vals):
        """
        If we create from template we send default code by context
        """
        default_code = vals.get('default_code', False)
        if default_code:
            return super(ProductTemplate, self.with_context(
                default_default_code=default_code)).create(vals)
        return super(ProductTemplate, self).create(vals)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code('product.default_code')

    default_code = fields.Char(
        required=True,
        default=_get_default_code,
    )
