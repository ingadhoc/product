##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    add_to_name = fields.Boolean(
        'Add To Name?',
        help='If false, then only attributes with more than one value will be'
        ' added to product displayed name, if true, all attributes will be '
        'added to product displayed name "Add attribute value"'
        ' to product displayed name',
    )
