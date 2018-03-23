##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class product_template(models.Model):
    _inherit = 'product.template'

    other_sale_description = fields.Char(
        'Other Sale Description',
    )
