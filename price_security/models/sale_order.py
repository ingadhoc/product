##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
            raise UserError(_(
                'Selected pricelist priority can not be higher than pircelist '
                'configured on partner'
            ))
        if (
                self.partner_id.property_payment_term_id and
                self.payment_term_id and
                self.partner_id.property_payment_term_id.sequence <
                self.payment_term_id.sequence):
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
