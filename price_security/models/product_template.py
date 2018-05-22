##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_modify_prices = fields.Boolean(
        help="If checked all users can modify the "
        "price of this product in a sale order or invoice.",
        string='Can modify prices')
