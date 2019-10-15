##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api
from odoo.tools import float_compare


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    product_can_modify_prices = fields.Boolean(
        related='product_id.can_modify_prices',
        string='Product Can modify prices',
        )

    @api.constrains(
        'discount',
        'product_id'
        # this is a related none stored field
        # 'product_can_modify_prices'
    )
    def check_discount(self):
        if not self.user_has_groups('price_security.group_restrict_prices'):
            return True
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for il in self:
            # only customer invoices
            if il.invoice_id and il.invoice_id.type in (
                    'out_invoice', 'out_refund'
            ) and not il.product_can_modify_prices:
                # chequeamos si la orden de venta permitió un descuento mayor
                if any(
                        float_compare(
                        x.discount, il.discount, precision_digits=precision
                        ) >= 0 for x in il.sale_line_ids):
                    return True
                il.env.user.check_discount(
                    il.discount,
                    il.invoice_id.partner_id.property_product_pricelist.id)
