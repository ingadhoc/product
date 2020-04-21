##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _prepare_purchase_order_line(
            self, product_id, product_qty, product_uom, values, po, supplier):
        """ We modify this method to set the uom select for purchase in the
        UOMs of the product, by de onchange selected the correctly
        of the line product to avoid an error then when validate in the
         creation of the purchase line.
        """
        res = super()._prepare_purchase_order_line(
            product_id, product_qty,
            product_uom, values, po, supplier)

        purchase_line = self.env['purchase.order.line'].new(res)
        purchase_line.onchange_product_id()
        res['product_uom'] = purchase_line.product_uom.id
        return res
