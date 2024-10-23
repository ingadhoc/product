# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, po):
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, po
        )
        if vals['price_unit'] == 0:
            vals['price_unit'] = product_id.standard_price

        return vals
