##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_attribute_template_id = fields.Many2one(
        'product.attribute.template',
        string='Product attributes template',
    )
