# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.osv import fields as old_fields
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # we do this so that we can show prices with or without taxe without
    # needing a pricelist
    @api.multi
    def _product_lst_price(self):
        # res = {}
        context = self._context
        company_id = (
            context.get('company_id') or self.env.user.company_id.id)
        taxes_included = context.get('taxes_included')

        for product in self:
            lst_price = product.list_price
            if taxes_included:
                lst_price = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                        lst_price, product=product)['total_included']
            product.lst_price = lst_price

    @api.model
    def _search_products_by_lst_price(self, operator, value):
        # TODO improove this, for now, at least we return products without
        # considering taxes
        return [('list_price', operator, value)]

    lst_price = fields.Float(
        compute='_product_lst_price',
        search='_search_products_by_lst_price',
        string='Public Price',
        # readonly=True,
        digits=dp.get_precision('Product Price')
    )

    taxed_lst_price = fields.Float(
        string='Taxed Sale Price',
        compute='get_taxed_lst_price',
        digits=dp.get_precision('Product Price'),
    )

    @api.multi
    @api.depends('taxes_id', 'lst_price')
    def get_taxed_lst_price(self):
        company_id = (
            self._context.get('company_id') or
            self.env.user.company_id.id)
        taxes_included = self._context.get('taxes_included')
        for product in self:
            # if taxes_included lst_price already has taxes included
            if taxes_included:
                product.taxed_lst_price = product.lst_price
            else:
                product.taxed_lst_price = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                        product.lst_price,
                        self.env.user.company_id.currency_id,
                        product=product)['total_included']


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # we do this so that we can show prices with or without taxe without
    # needing a pricelist
    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = super(ProductProduct, self)._product_lst_price(
            cr, uid, ids, name, arg, context=context)
        if not context.get('taxes_included'):
            return res
        company_id = (
            context.get('company_id') or
            self.pool['res.users'].browse(cr, uid, uid, context).
            company_id.id)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = product.taxes_id.filtered(
                lambda x: x.company_id.id == company_id).compute_all(
                res[product.id], product=product.id)['total_included']
        return res

    def _set_product_lst_price(
            self, cr, uid, id, name, value, args, context=None):
        if context.get('taxes_included'):
            raise UserError(_(
                "You can not set list price if you are working with 'Taxes "
                "Included' in the context"))
        return super(ProductProduct, self)._set_product_lst_price(
            cr, uid, id, name, value, args, context=context)

    _columns = {
        'lst_price': old_fields.function(
            _product_lst_price, fnct_inv=_set_product_lst_price, type='float',
            string='Public Price',
            digits_compute=dp.get_precision('Product Price')),
    }
