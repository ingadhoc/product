##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class DiscountRestriction(models.Model):
    _name = 'res.users.discount_restriction'
    _description = 'Discount Restriction'

    pricelist_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        ondelete='cascade',)
    min_discount = fields.Float('Min. Discount', required=True)
    max_discount = fields.Float('Max. Discount', required=True)
    user_id = fields.Many2one(
        'res.users',
        'User',
        index=True,
        required=True,
        ondelete='cascade',
    )
