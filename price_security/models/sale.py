# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


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

    @api.one
    @api.onchange('price_unit_readonly')
    def onchange_price_unit_readonly(self):
        self.price_unit = self.price_unit_readonly

    @api.one
    @api.onchange('tax_id_readonly')
    def onchange_tax_id_readonly(self):
        self.tax_id = self.tax_id_readonly

    @api.one
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
                self.order_id.pricelist_id.id)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.constrains(
        'pricelist_id',
        'payment_term_id',
        'partner_id')
    def check_priority(self):
        if not self.user_has_groups('price_security.group_restrict_prices'):
            return True
        if (
                self.partner_id.property_product_pricelist and
                self.pricelist_id and
                self.partner_id.property_product_pricelist.sequence <
                self.pricelist_id.sequence):
            raise Warning(_(
                'Selected pricelist priority can not be higher than pircelist '
                'configured on partner'
            ))
        if (
                self.partner_id.property_payment_term_id and
                self.payment_term_id and
                self.partner_id.property_payment_term_id.sequence <
                self.payment_term_id.sequence):
            raise Warning(_(
                'Selected payment term priority can not be higher than '
                'payment term configured on partner'
            ))

    @api.onchange('partner_id')
    def check_partner_pricelist_change(self):
        pricelist = self.partner_id.property_product_pricelist
        if self.order_line and pricelist != self._origin.pricelist_id:
            self.partner_id = self._origin.partner_id
            return {'warning': {'title': "Warning", 'message': "You can"
                                " not change partner if there are sale lines"
                                " and pricelist is going to be changed"}}
