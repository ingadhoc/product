# -*- encoding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def migrate(cr, version):
    print 'Migrating product_uom_prices'
    if not version:
        return
    create_product_sale_uom(cr)

#     # no need to install this module this module as dependency manage it
#     # new module added as dependency
#     # install_module(cr, 'product_sale_uom')


def create_product_sale_uom(cr):
    registry = RegistryManager.get(cr.dbname)
    by_uom_template_ids = registry['product.template'].search(
        cr, SUPERUSER_ID,
        [('list_price_type', '=', 'by_uom')], {})
    for template_id in by_uom_template_ids:
        template_read = registry['product.template'].read(
            cr, SUPERUSER_ID, template_id, ['uom_id', 'list_price'])
        uom_id = template_read['uom_id'][0]
        price = template_read['list_price']
        print 'template_id', template_id
        print 'template_read', template_read
        print 'uom_id', uom_id
        print 'price', price

        registry['product.sale.uom'].create(
            cr, SUPERUSER_ID, {
                'sequence': 15,
                'product_tmpl_id': template_id,
                'uom_id': uom_id,
                'price': price,
            }, {})

    # migrate by_uom_currency
    by_uom_template_ids = registry['product.template'].search(
        cr, SUPERUSER_ID,
        [('list_price_type', '=', 'by_uom_currency')], {})
    for template_id in by_uom_template_ids:
        template_read = registry['product.template'].read(
            cr, SUPERUSER_ID, template_id,
            ['uom_id', 'other_currency_list_price'])
        uom_id = template_read['uom_id'][0]
        price = template_read['other_currency_list_price']
        print 'template_id', template_id
        print 'template_read', template_read
        print 'uom_id', uom_id
        print 'price', price

        registry['product.sale.uom'].create(
            cr, SUPERUSER_ID, {
                'sequence': 0,
                'product_tmpl_id': template_id,
                'uom_id': uom_id,
                'price': price,
            }, {})
    return True

# def install_module(cr, module):
#     registry = RegistryManager.get(cr.dbname)
#     model = registry['ir.module.module']
#     module_ids = model.search(
#         cr, SUPERUSER_ID,
#         [('name', '=', module)], {})
#     print 'install module %s' % module
#     print 'ids for module: %s' % module_ids
#     model.button_install(
#         cr, SUPERUSER_ID, module_ids, {})
#     print 'module installed'
