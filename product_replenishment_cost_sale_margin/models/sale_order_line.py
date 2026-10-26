from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_purchase_price(self):
        super()._compute_purchase_price()
        # since 20.0 core leaves no cost on delivery, down payment and discount lines
        for line in self.filtered(lambda line: line.product_id and line._is_product_line()):
            order_id = line.order_id
            product_id = line.product_id
            product_uom_id = line.product_uom_id
            if product_id.replenishment_cost:
                frm_cur = product_id.currency_id
                to_cur = order_id.currency_id
                purchase_price = product_id.replenishment_cost
                if product_uom_id != product_id.uom_id:
                    purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
                line.purchase_price = frm_cur._convert(
                    purchase_price,
                    to_cur,
                    order_id.company_id or self.env.company,
                    order_id.date_order or fields.Date.today(),
                    round=False,
                )
