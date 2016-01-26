# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class price_type(models.Model):
    _inherit = "product.price.type"

    # @api.model
    # def _get_field_currency(self, fname):
    #     """
    #     Because of bad implementation of this and calls from, for eg.
    #     website_sale, and because we want to deactivate this price type, we
    #     overwrite this function, if not price_type found and requested is
    #     "list_price" then we return computed
    #     """
    #     field = self.search([('field', '=', fname)], limit=1)
    #     if not field and fname == 'list_price':
    #         field = self.search(
    #             [('field', '=', 'computed_list_price')], limit=1)
    #     return field.currency_id

    def search(
            self, cr, uid, args, offset=0, limit=None,
            order=None, context=None, count=False):
        """
        Because of bad implementation of many searches of 'list_price', some
        hardecoded other not, for eg on "on_change_unit_amount" of
        account_analytic_account, on website_sale.
        if not price_type found and requested is "list_price" then we search
        "computed_list_price"
        """
        res = super(price_type, self).search(
            cr, uid, args, offset=offset, limit=limit,
            order=order, context=context, count=count)
        if not res:
            for field, operator, value in args:
                if field == 'field' and 'list_price' in value:
                    args = ['|', ('field', '=', 'computed_list_price')] + args
                    return super(price_type, self).search(
                        cr, uid, args, offset=offset, limit=limit,
                        order=order, context=context, count=count)
        return res


# class product_pricelist_item(models.Model):
#     _inherit = "product.pricelist.item"

#     def _get_default_base(self, cr, uid, fields, context=None):
#         """
#         Modificamos el default type para que si list_price esta desactivado
#         ofrezca computed_list_price
#         """
#         list_price_id = super(
#             product_pricelist_item, self)._get_default_base(
#             cr, uid, fields, context)
#         if not list_price_id and fields.get('type') == 'sale':
#             list_price_id = self.pool['product.price.type'].search(
#                 cr, uid,
#                 [('field', '=', 'computed_list_price')],
#                 limit=1, context=context)
#         return list_price_id

#     _defaults = {
#         'base': _get_default_base,
#         }
