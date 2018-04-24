##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    active = fields.Boolean(track_visibility='onchange')
