##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    sellers_product_code = fields.Char(
        related='seller_ids.product_code',
        string="Vendor Product Code",
    )
