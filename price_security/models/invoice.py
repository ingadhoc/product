# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    # we add this fields instead of making original readonly because we need
    # on change to change values, we make readonly in view because sometimes
    # we want them to be writeable
    invoice_line_tax_id_readonly = fields.Many2many(
        related='invoice_line_tax_id',
    )
    price_unit_readonly = fields.Float(
        related='price_unit',
    )
    product_can_modify_prices = fields.Boolean(
        related='product_id.can_modify_prices',
        string='Product Can modify prices')

    @api.one
    @api.constrains(
        'discount', 'product_can_modify_prices')
    def check_discount(self):
        if (
                self.user_has_groups(
                    'price_security.group_restrict_prices') and
                not self.product_can_modify_prices and self.invoice_id
        ):
            self.env.user.check_discount(
                self.discount,
                self.invoice_id.partner_id.property_product_pricelist.id)
