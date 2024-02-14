# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        vals = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        supplier = values['supplier']
        po = line.order_id
        price_unit = self.env['account.tax']._fix_tax_included_price_company(supplier.net_price, product_id.supplier_taxes_id, line.taxes_id, company_id) if supplier else 0.0
        if price_unit and supplier and po.currency_id and supplier.currency_id != po.currency_id:
            price_unit = supplier.currency_id._convert(price_unit, po.currency_id, po.company_id, po.date_order or fields.Date.today())
        vals['price_unit'] = price_unit

        return vals
