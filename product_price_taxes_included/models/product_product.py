##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.osv import fields as old_fields
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


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
