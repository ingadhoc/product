# -*- encoding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def get_legacy_name(original_name, version):
    return 'legacy_%s_%s' % (version.replace('.', '_'), original_name)


def set_value(cr, model, table, field, value, condition):
    print 'Set value %s on field %s on table %s' % (
        value, field, table)
    cr.execute('SELECT id '
               'FROM %(table)s '
               '%(condition)s' % {
                   'table': table,
                   'condition': condition,
               })
    for row in cr.fetchall():
        model.write(cr, SUPERUSER_ID, row[0], {field: value})


def migrate(cr, version):
    print 'Migrating product_uom_prices'
    if not version:
        return
    registry = RegistryManager.get(cr.dbname)

    # we intall this because previous version requires price_currency so we
    # need to install this auto_install module
    install_module(cr, 'product_uom_prices_currency')

    # get list_price currency
    cr.execute(
        "SELECT currency_id FROM product_price_type WHERE field = 'list_price'")
    currency_id = cr.fetchall()[0][0]
    print 'currency_id', currency_id

    model = 'product.template'
    table = 'product_template'
    field = "list_price_type"

    # set value for "by_uom"
    value = "by_uom"
    use_uom_prices_columns = get_legacy_name('use_uom_prices', version)
    print 'use_uom_prices_columns', use_uom_prices_columns
    condition = "WHERE %s and other_currency_id = %s" % (
        use_uom_prices_columns, currency_id)
    set_value(
        cr,
        registry[model],
        table,
        field,
        value,
        condition,
    )

    # set value for "by_uom_currency"
    value = "by_uom_currency"
    use_uom_prices_columns = get_legacy_name('use_uom_prices', version)
    print 'use_uom_prices_columns', use_uom_prices_columns
    vals = "SET %s = '%s'" % (field, value)
    condition = "WHERE %s and other_currency_id != %s" % (
        use_uom_prices_columns, currency_id)

    cr.execute("UPDATE product_template %s %s" % (vals, condition))


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
