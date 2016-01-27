# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class product_pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model
    def _price_get_multi(self, pricelist, products_by_qty_by_partner):
        res = super(product_pricelist, self)._price_get_multi(
            pricelist, products_by_qty_by_partner)
        if self._context.get('taxes_included'):
            company_id = (
                self._context.get('company_id') or self.env.user.company_id.id)
            for product, qty, partner in products_by_qty_by_partner:
                if pricelist.type == 'purchase':
                    res[product.id] = product.supplier_taxes_id.filtered(
                        lambda x: x.company_id.id == company_id).compute_all(
                        res[product.id], qty, product=product,
                        partner=partner)['total_included']
                else:
                    res[product.id] = product.taxes_id.filtered(
                        lambda x: x.company_id.id == company_id).compute_all(
                        res[product.id], qty, product=product,
                        partner=partner)['total_included']
        return res

    # @api.model
    # def _price_rule_get_multi(self, pricelist, products_by_qty_by_partner):
    #     res = super(product_pricelist, self)._price_rule_get_multi(
    #         pricelist, products_by_qty_by_partner)
    #     print '_price_rule_get_multi', res
    #     return res
# class product_product(models.Model):
#     _inherit = "product.product"

#     def _product_price(self, cr, uid, ids, name, arg, context=None):
#         print 'product_product', cr, uid, ids, name, arg, context
#         super(product_product, self)._product_price(
#             cr, uid, ids, name, arg, context)


# class product_template(models.Model):
#     _inherit = "product.template"

#     # 'price': fields.function(_product_template_price, type='float', string='Price', digits_compute=dp.get_precision('Product Price')),
#     price = fields.Float(string="12312", compute='_product_template_price')

#     @api.multi
#     def _product_template_price(self):
#     # def _product_template_price(self, cr, uid, ids, name, arg, context=None):
#         print 'prod template'
#         print 'prod template'
#         print 'prod template'
#         print 'prod template'
#         # print 'prod template', cr, uid, ids, name, arg, context
#         return super(product_template, self)._product_template_price(
#             False, False)
#         # super(product_template, self)._product_template_price(
#             # cr, uid, ids, name, arg, context)
