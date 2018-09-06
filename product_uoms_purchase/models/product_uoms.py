##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductUoms(models.Model):
    _inherit = 'product.uoms'

    purchase_ok = fields.Boolean(
        default=True,
    )
