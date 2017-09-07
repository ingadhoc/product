# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError


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

    @api.multi
    @api.onchange('price_unit_readonly')
    def onchange_price_unit_readonly(self):
        for rec in self:
            rec.price_unit = rec.price_unit_readonly

    @api.multi
    @api.onchange('tax_id_readonly')
    def onchange_tax_id_readonly(self):
        for rec in self:
            rec.tax_id = rec.tax_id_readonly

    @api.multi
    @api.constrains(
        'discount',
        'product_id',
        # this is a related none stored field
        # 'product_can_modify_prices'
    )
    def check_discount(self):
        for rec in self:
            if (rec.user_has_groups('price_security.group_restrict_prices'
                                    ) and not rec.product_can_modify_prices):
                self.env.user.check_discount(
                    rec.discount,
                    rec.order_id.pricelist_id.id)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.constrains(
        'pricelist_id',
        'payment_term_id',
        'partner_id')
    def check_priority(self):
        for rec in self:
            if not rec.user_has_groups('price_security.group_restrict_prices'):
                return True
            if (
                    rec.partner_id.property_product_pricelist and
                    rec.pricelist_id and
                    rec.partner_id.property_product_pricelist.sequence <
                    rec.pricelist_id.sequence):
                raise UserError(_(
                    'Selected pricelist priority can not be higher than '
                    'pricelist configured on partner'
                ))
            if (
                    rec.partner_id.property_payment_term_id and
                    rec.payment_term_id and
                    rec.partner_id.property_payment_term_id.sequence <
                    rec.payment_term_id.sequence):
                raise UserError(_(
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
