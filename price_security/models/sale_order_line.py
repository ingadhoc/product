##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_can_modify_prices = fields.Boolean(
        related='product_id.can_modify_prices',
        )

    @api.constrains(
        'discount',
        'product_id',
        # this is a related none stored field
        # 'product_can_modify_prices'
    )
    def check_discount(self):
        if not self.user_has_groups(
                'price_security.group_restrict_prices'):
            return True
        for rec in self.filtered(lambda x: not x.product_can_modify_prices):
            self.env.user.check_discount(
                rec.discount,
                rec.order_id.pricelist_id.id,
                so_line=rec)
