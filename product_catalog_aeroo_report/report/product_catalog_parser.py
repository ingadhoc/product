# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import time
from openerp import _
from openerp.report.report_sxw import rml_parse
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Parser(rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)

        lang = context.get('lang', 'es_ES')

        self.print_product_uom = context.get('print_product_uom', False)
        self.product_type = context.get('product_type', 'product.product')
        self.prod_display_type = context.get('prod_display_type', False)
        pricelist_ids = context.get('pricelist_ids', [])
        pricelists = self.pool['product.pricelist'].browse(
            cr, uid, pricelist_ids, context=context)

        categories_order = context.get('categories_order', '')

        # Get categories ordered
        category_type = context.get('category_type', False)
        if category_type == 'public_category':
            categories = self.pool['product.public.category']
        else:
            categories = self.pool['product.category']
        category_ids = context.get('category_ids', [])
        category_ids = categories.search(
            cr, uid, [('id', 'in', category_ids)],
            order=categories_order, context=context)
        categories = categories.browse(
            cr, uid, category_ids, context=context)

        products = self.get_products(category_ids, context=context)
        company_id = self.pool['res.users'].browse(
            cr, uid, [uid])[0].company_id
        self.localcontext.update({
            'lang': lang,
            'categories': categories,
            'products': products,
            'print_product_uom': self.print_product_uom,
            'product_type': self.product_type,
            'prod_display_type': self.prod_display_type,
            'company_logo': company_id.logo,
            'pricelists': pricelists,
            'today': time.localtime(),
            'get_price': self.get_price,
            'get_description': self.get_description,
            'get_products': self.get_products,
            'context': context,
            'field_value_get': self.field_value_get,
        })

    def field_value_get(self, product, field, context=None):
        # TODO hacer funcioal esto en el reporte ods. El problema es que
        # deberiamos usar export_data en vez de read para poder elegir que ver
        # del padre, por ejemplo "categ_id/name"
        if not context:
            context = {}
        product_obj = self.pool.get(self.product_type)
        field_value = product_obj.read(
            self.cr, self.uid, [product.id], [field], context=context)
        return field_value[0].get(field, '')

    def get_price(self, product, pricelist, context=None):
        if not context:
            context = {}
        context['pricelist'] = pricelist.id
        product_obj = self.pool[self.product_type]
        sale_uom = self.pool['product.template'].fields_get(
            self.cr, self.uid, ['sale_uom_ids'])
        if sale_uom and product.sale_uom_ids:
            context['uom'] = product.sale_uom_ids[0].uom_id.id
        price = product_obj.browse(
            self.cr, self.uid, [product.id], context=context).price
        return price

    def get_description(self, product, print_product_uom, context=None):

        sale_uom = self.pool['product.template'].fields_get(
            self.cr, self.uid, ['sale_uom_ids'])
        if not print_product_uom:
            return product.display_name
        if sale_uom and product.sale_uom_ids:
            main_uom = product.sale_uom_ids[0].uom_id
        else:
            main_uom = product.uom_id
        description = _('%s (%s)' % (product.
                                     display_name, main_uom.display_name))
        if sale_uom and len(product.sale_uom_ids) > 1:
            description = _('%s. Also available in %s') % (
                description, ', '.join(
                    product.sale_uom_ids.filtered(
                        lambda x: x.uom_id != main_uom).
                    mapped('uom_id.display_name')))

        return description

    def get_products(self, category_ids, context=None):
        if not isinstance(category_ids, list):
            category_ids = [category_ids]

        if not context:
            context = {}
        order = context.get('products_order', '')
        only_with_stock = context.get('only_with_stock', False)
        category_type = context.get('category_type', False)
        if category_type == 'public_category':
            domain = [('public_categ_ids', 'in', category_ids)]
        else:
            domain = [('categ_id', 'in', category_ids)]
        if only_with_stock:
            domain.append(('qty_available', '>', 0))

        product_ids = self.pool[self.product_type].search(
            self.cr, self.uid, domain, order=order, context=context)

        products = self.pool[self.product_type].browse(
            self.cr, self.uid, product_ids, context=context)
        return products
