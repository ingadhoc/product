##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    active = fields.Boolean(tracking=True)
    sellers_product_code = fields.Char(
        'Vendor Product Code',
        related='seller_ids.product_code',
    )
    warranty = fields.Float()
