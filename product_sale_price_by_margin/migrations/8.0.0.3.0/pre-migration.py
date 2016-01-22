# -*- encoding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def copy_column(cr, model, table, target_field, source_field, condition):
    print 'Making copy of columne %s to column %s' % (
        source_field, target_field)
    cr.execute('SELECT id, %(field)s '
               'FROM %(table)s '
               '%(condition)s' % {
                   'table': table,
                   'field': source_field,
                   'condition': condition,
               })
    for row in cr.fetchall():
        model.write(cr, SUPERUSER_ID, row[0], {target_field: row[1]})
        # model.write(cr, SUPERUSER_ID, row[0], {target_field: [(4, row[1])]})


def migrate(cr, version):
    print 'Migrating product_sale_price_by_margin'
    if not version:
        return
    registry = RegistryManager.get(cr.dbname)
    model = 'product.template'
    table = 'product_template'
    source_field = "manual_list_price"
    target_field = "list_price"
    condition = "WHERE list_price_type = 'manual'"
    copy_column(
        cr,
        registry[model],
        table,
        source_field,
        target_field,
        condition,
    )
