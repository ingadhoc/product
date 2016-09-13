# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, _
from openerp import fields as new_fields
from openerp.osv import fields
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = 'product.template'

    # we do this so that we can show prices with or without taxe without
    # needing a pricelist
    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        company_id = (
            context.get('company_id') or
            self.pool['res.users'].browse(cr, uid, uid, context).
            company_id.id)
        taxes_included = context.get('taxes_included')

        for product in self.browse(cr, uid, ids, context=context):
            lst_price = product.list_price
            if taxes_included:
                lst_price = self.pool['account.tax'].compute_all(
                    cr, uid, product.taxes_id.filtered(
                        lambda x: x.company_id.id == company_id),
                    lst_price, product_id=product)['total_included']
            res[product.id] = lst_price
        return res

    _columns = {
        'lst_price': fields.function(
            _product_lst_price, type='float',
            string='Public Price',
            readonly=True,
            digits_compute=dp.get_precision('Product Price')),
    }

    taxed_lst_price = new_fields.Float(
        string='Taxed Sale Price',
        compute='get_taxed_lst_price'
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
                        1.0,
                        product=product)['total_included']


class product_product(models.Model):
    _inherit = 'product.product'

    # we do this so that we can show prices with or without taxe without
    # needing a pricelist
    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = super(product_product, self)._product_lst_price(
            cr, uid, ids, name, arg, context=context)
        if not context.get('taxes_included'):
            return res
        company_id = (
            context.get('company_id') or
            self.pool['res.users'].browse(cr, uid, uid, context).
            company_id.id)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = self.pool['account.tax'].compute_all(
                cr, uid, product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id),
                res[product.id], product_id=product)['total_included']
        return res

    def _set_product_lst_price(
            self, cr, uid, id, name, value, args, context=None):
        if context.get('taxes_included'):
            raise Warning(_(
                "You can not set list price if you are working with 'Taxes "
                "Included' in the context"))
        return super(product_product, self)._set_product_lst_price(
            cr, uid, id, name, value, args, context=context)

    _columns = {
        'lst_price': fields.function(
            _product_lst_price, fnct_inv=_set_product_lst_price, type='float',
            string='Public Price',
            digits_compute=dp.get_precision('Product Price')),
    }
