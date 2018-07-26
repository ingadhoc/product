##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _


class Parser(models.AbstractModel):
    _inherit = 'report.report_aeroo.abstract'

    _name = 'report.product_catalog_parser'

    @api.model
    def aeroo_report(self, docids, data):
        self.print_product_uom = self._context.get('print_product_uom', False)
        self.product_type = self._context.get(
            'product_type', 'product.product')
        self.prod_display_type = self._context.get('prod_display_type', False)
        pricelist_ids = self._context.get('pricelist_ids', [])
        categories_order = self._context.get('categories_order', '')
        pricelists = self.env['product.pricelist'].browse(pricelist_ids)

        # Get categories ordered
        category_type = self._context.get('category_type', False)
        if category_type == 'public_category':
            categories = self.env['product.public.category']
        else:
            categories = self.env['product.category']
        category_ids = self._context.get('category_ids', [])
        categories = categories.search([('id', 'in', category_ids)],
                                       order=categories_order)
        products = self.get_products(category_ids)
        self = self.with_context(
            products=products,
            categories=categories,
            pricelists=pricelists,
            company_logo=self.env.user.company_id.logo,
            print_product_uom=self.print_product_uom,
            product_type=self.product_type,
            prod_display_type=self.prod_display_type,
            today=fields.Date.today(),
            get_price=self.get_price,
            get_description=self.get_description,
            get_products=self.get_products,
            context=self._context,
            field_value_get=self.field_value_get,
        )
        return super(Parser, self).aeroo_report(docids, data)

    def field_value_get(self, product, field):
        # TODO hacer funcioal esto en el reporte ods. El problema es que
        # deberiamos usar export_data en vez de read para poder elegir que ver
        # del padre, por ejemplo "categ_id/name"
        product_obj = self.env[self.product_type]
        field_value = product_obj.read(
            [product.id], [field])
        return field_value[0].get(field, '')

    def get_price(self, product, pricelist):
        product_obj = self.env[self.product_type].with_context(
            pricelist=pricelist.id)
        sale_uom = self.env['product.template'].fields_get(
            ['sale_uom_ids'])
        if sale_uom and product.sale_uom_ids:
            product_obj = product_obj.with_context(
                uom=product.sale_uom_ids[0].uom_id.id)
        return product_obj.browse([product.id]).price

    def get_description(self, product, print_product_uom):

        sale_uom = self.env['product.template'].fields_get(
            ['sale_uom_ids'])
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

    def get_products(self, category_ids):
        if not isinstance(category_ids, list):
            category_ids = [category_ids]
        order = self._context.get('products_order', '')
        only_with_stock = self._context.get('only_with_stock', False)
        category_type = self._context.get('category_type', False)
        if category_type == 'public_category':
            domain = [('public_categ_ids', 'in', category_ids)]
        else:
            domain = [('categ_id', 'in', category_ids)]
        if only_with_stock:
            domain.append(('qty_available', '>', 0))

        products = self.env[self.product_type].search(
            domain, order=order)
        return products
