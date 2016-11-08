# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            product = self.product_id.with_context(
                partner_id=self.order_id.partner_id.id)
            if 'domain' not in res:
                res['domain'] = {}
            res['domain']['product_uom'] = [
                ('id', 'in', [x.uom_id.id for x in product.uom_price_ids] +
                    [product.uom_id.id] + [product.uom_po_id.id])]
        return res
