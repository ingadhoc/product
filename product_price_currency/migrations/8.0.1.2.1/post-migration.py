# -*- encoding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def set_value(cr, model, table, field, value, condition):
    print 'Set value %s on field %s on table %s' % (
        value, field, table)
    cr.execute('SELECT id, list_price '
               'FROM %(table)s '
               '%(condition)s' % {
                   'table': table,
                   'condition': condition,
               })
    for row in cr.fetchall():
        print 'row', row
        model.write(cr, SUPERUSER_ID, row[0], {
            field: value,
            'other_currency_list_price': row[1]
            })


def migrate(cr, version):
    print 'Migrating product_uom_prices'
    if not version:
        return
    # no lo podemos auto instalar porque nos da une error hasta que no se
    # termine de actualziar todo
    # install_module(cr, 'product_template_tree_prices')

    registry = RegistryManager.get(cr.dbname)

    cr.execute(
        "SELECT currency_id FROM product_price_type WHERE field = 'list_price'")
    currency_id = cr.fetchall()[0][0]
    print 'currency_id', currency_id

    model = 'product.template'
    table = 'product_template'
    field = "list_price_type"
    value = "other_currency"
    condition = "WHERE other_currency_id != %s" % currency_id
    set_value(
        cr,
        registry[model],
        table,
        field,
        value,
        condition,
    )


def install_module(cr, module):
    registry = RegistryManager.get(cr.dbname)
    model = registry['ir.module.module']
    module_ids = model.search(
        cr, SUPERUSER_ID,
        [('name', '=', module)], {})
    print 'install module %s' % module
    print 'ids for module: %s' % module_ids
    model.button_install(
        cr, SUPERUSER_ID, module_ids, {})
    print 'module installed'
