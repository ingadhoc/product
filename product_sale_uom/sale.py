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
    def product_id_change(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False):
        # because sale_stock module delete uom when colling this method, we
        # add it in context con module 'sale_stock_product_uom_prices'
        if not uom:
            uom = self._context.get('preserve_uom', False)
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag)

        if product:
            context_partner = {'lang': lang, 'partner_id': partner_id}
            product = self.env['product.product'].with_context(
                context_partner).browse(
                product)

            # we can use line on self but we should use self.ensure_one()
            sale_product_uoms = self.get_product_uoms(product)
            if sale_product_uoms:
                if not uom:
                    uom_id = sale_product_uoms[0].id
                    res['value']['product_uom'] = uom_id

                # we do this because odoo overwrite view domain
                if 'domain' not in res:
                    res['domain'] = {}
                res['domain']['product_uom'] = [
                    ('id', 'in', sale_product_uoms.ids)]
        return res
