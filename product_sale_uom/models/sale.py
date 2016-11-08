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
        self.uom_unit_ids = self.get_product_uoms(self.product_id)

    @api.model
    def get_product_uoms(self, product):
        """
        if product has uoms configured, we use them
        if not, we choose all uoms from uom_id category (first the product uom)
        """
        # we can not use product.mapped('sale_uom_ids.uom_id') becuase it loose
        # order of sale_uom_ids
        return (
            self.env['product.uom'].browse(
                [x.uom_id.id for x in product.sale_uom_ids]) or
            (product.uom_id + self.env['product.uom'].search([
                ('category_id', '=', product.uom_id.category_id.id),
                ('id', '!=', product.uom_id.id),
            ]))
        )

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        uom = self.product_uom.id
        # because sale_stock module delete uom when colling this method, we
        # add it in context con module 'sale_stock_product_uom_prices'
        # if not self.product_uom.id:
        #     uom = self._context.get('preserve_uom', False)
        product_uom_domain = None
        if self.product_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id)

            # we can use line on self but we should use self.ensure_one()
            sale_product_uoms = self.get_product_uoms(product)
            if sale_product_uoms:
                if not uom:
                    uom = sale_product_uoms[0].id

                # we do this because odoo overwrite view domain
                product_uom_domain = [('id', 'in', sale_product_uoms.ids)]
        res = super(SaleOrderLine, self).product_id_change()
        if uom:
            self.product_uom = uom
        if product_uom_domain:
            res = {'domain': {'product_uom': product_uom_domain}}
        return res
