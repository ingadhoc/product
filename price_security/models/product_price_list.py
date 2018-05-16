##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    sequence = fields.Integer(
        string='Sequence')
