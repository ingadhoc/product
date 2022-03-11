from odoo import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id.replenishment_cost')
    def _compute_purchase_price(self):
        super()._compute_purchase_price()
        for line in self.filtered('product_id'):
            order_id = line.order_id
            product_id = line.product_id
            product_uom_id = line.product_uom
            if product_id.replenishment_cost:
                frm_cur = product_id.currency_id
                to_cur = order_id.currency_id
                purchase_price = product_id.replenishment_cost
                if product_uom_id != product_id.uom_id:
                    purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
                line.purchase_price = frm_cur._convert(
                    purchase_price, to_cur, order_id.company_id or self.env.company,
                    order_id.date_order or fields.Date.today(), round=False)
                

    def _convert_price(self, product_cost, from_uom):
        if not product_cost:
            if not self.purchase_price:
                return product_cost
        if self.product_id.replenishment_cost:
            frm_cur = self.product_id.currency_id
            to_cur = self.currency_id or self.order_id.currency_id
            purchase_price = self.product_id.replenishment_cost
            if self.product_uom != from_uom:
                purchase_price = from_uom._compute_price(purchase_price, self.product_uom)
            return frm_cur._convert(
                purchase_price, to_cur,
                self.order_id.company_id or self.env.company,
                self.order_id.date_order or fields.Date.today(), round=False)
        else:
            return super()._convert_price(product_cost, from_uom)
