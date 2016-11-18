# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    uom_unit_ids = fields.Many2many('product.uom', compute='_get_units')

    @api.one
    @api.depends('product_id')
    def _get_units(self):
        if self.product_id:
            self.uom_unit_ids = self.product_id.get_product_uoms(
                self.product_id.uom_id)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        product_uom = None
        product_uom_domain = None
        if self.product_id:
            product = self.product_id

            sale_product_uoms = product.get_product_uoms(product.uom_id)
            if sale_product_uoms:
                product_uom = sale_product_uoms[0].id

                # we do this because odoo overwrite view domain
                product_uom_domain = [('id', 'in', sale_product_uoms.ids)]
        res = super(SaleOrderLine, self).product_id_change()
        if product_uom:
            self.product_uom = product_uom
        if product_uom_domain:
            res = {'domain': {'product_uom': product_uom_domain}}
        return res
