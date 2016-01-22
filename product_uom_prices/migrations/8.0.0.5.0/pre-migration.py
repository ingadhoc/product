# -*- encoding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


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
    model = 'product.template'
    table = 'product_template'
    field = "list_price_type"
    value = "by_uom"
    condition = "WHERE use_uom_prices"
    set_value(
        cr,
        registry[model],
        table,
        field,
        value,
        condition,
    )
