##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # we add this fields instead of making original readonly because we need
    # on change to change values, we make readonly in view because sometimes
    # we want them to be writeable
    price_unit_readonly = fields.Float(
        related='price_unit',
    )
    tax_id_readonly = fields.Many2many(
        related='tax_id',
    )
    product_can_modify_prices = fields.Boolean(
        related='product_id.can_modify_prices',
        readonly=True,
        string='Product Can modify prices')

    @api.onchange('price_unit_readonly')
    def onchange_price_unit_readonly(self):
        self.price_unit = self.price_unit_readonly

    @api.onchange('tax_id_readonly')
    def onchange_tax_id_readonly(self):
        self.tax_id = self.tax_id_readonly

    @api.constrains(
        'discount',
        'product_id',
        # this is a related none stored field
        # 'product_can_modify_prices'
    )
    def check_discount(self):

        if (self.user_has_groups('price_security.group_restrict_prices'
                                 ) and not self.product_can_modify_prices):
            self.env.user.check_discount(
                self.discount,
                self.order_id.pricelist_id.id,
                so_line=self)
