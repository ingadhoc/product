##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        super()._onchange_quantity()
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom)
        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            seller.net_price, self.product_id.supplier_taxes_id,
            self.taxes_id, self.company_id) if seller else 0.0
        if price_unit and seller and self.\
                order_id.currency_id and seller.\
                currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id,
                self.order_id.company_id,
                self.order_id.date_order or fields.Date.today())

        if seller and self.product_uom and seller.\
                product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(
                price_unit, self.product_uom)
        self.price_unit = price_unit
