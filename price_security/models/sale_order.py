##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, _
from odoo.exceptions import UserError
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains(
        'pricelist_id',
        'payment_term_id',
        'partner_id')
    def check_priority(self):
        if not self.user_has_groups('price_security.group_only_view'):
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
        if not self.user_has_groups('product.group_product_pricelist'):
            return
        pricelist = self.partner_id.property_product_pricelist
        if self.order_line and pricelist != self._origin.pricelist_id:
            if self.user_has_groups('price_security.group_only_view'):
                self.partner_id = self._origin.partner_id
                msj = _('You can not change partner if there are sale lines'
                        ' and pricelist is going to be changed')
            else:
                msj = _('The change of the customer generates a  change in the'
                        ' price list, remember to check / update the prices')
            return {'warning': {'title': "Warning", 'message': msj}}

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            if self.env.user.has_group('price_security.group_only_view'):
                fields = (arch.xpath("//field[@name='order_line']/tree//field[@name='price_unit']")
                                    + arch.xpath("//field[@name='order_line']/tree//field[@name='tax_id']")
                                    + arch.xpath("//field[@name='order_line']/form//field[@name='price_unit']")
                                    + arch.xpath("//field[@name='order_line']/form//field[@name='tax_id']")
                                    )
                for node in fields:
                    node.set('attrs', "{'readonly': [('product_can_modify_prices','=', False)]}")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['attrs'] = "{'readonly': [('product_can_modify_prices','=', False)]}"
                    node.set("modifiers", json.dumps(modifiers))
                    node.set('force_save', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['force_save'] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
