from odoo import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_margin(self, order_id, product_id, product_uom_id):
        if product_id.replenishment_cost:
            frm_cur = product_id.currency_id
            to_cur = order_id.pricelist_id.currency_id
            purchase_price = product_id.replenishment_cost
            if product_uom_id != product_id.uom_id:
                purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
            return frm_cur._convert(
                purchase_price, to_cur, order_id.company_id or self.env.user.company_id,
                order_id.date_order or fields.Date.today(), round=False)
        else:
            return super()._compute_margin(order_id, product_id, product_uom_id)

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        if product.replenishment_cost:
            frm_cur = product.currency_id
            to_cur = pricelist.currency_id
            purchase_price = product.replenishment_cost
            if product_uom != product.uom_id:
                purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
            price = frm_cur._convert(
                purchase_price, to_cur,
                self.order_id.company_id or self.env.user.company_id,
                date or fields.Date.today(), round=False)
        else:
            price = super()._get_purchase_price(pricelist, product, product_uom, date)
        return {'purchase_price': price}
