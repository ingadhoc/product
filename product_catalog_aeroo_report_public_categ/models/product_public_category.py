##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    _parent_order = 'sequence, name'

    parent_id = fields.Many2one(
        ondelete='restrict',
    )
    complete_name = fields.Char(
        'Complete Name',
        related='display_name',
        readonly=True,
    )
