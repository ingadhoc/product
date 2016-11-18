# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        product_uom = None
        product_uom_domain = None
        if self.product_id:
            product = self.product_id

            sale_product_uoms = product.get_product_uoms(product.uom_id)
            if sale_product_uoms:
                product_uom = sale_product_uoms[0]

                # we do this because odoo overwrite view domain
                product_uom_domain = [('id', 'in', sale_product_uoms.ids)]
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if product_uom:
            self.product_uom = product_uom
        if product_uom_domain:
            res = {'domain': {'product_uom': product_uom_domain}}
        return res
