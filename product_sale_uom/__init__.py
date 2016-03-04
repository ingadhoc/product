# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from . import product
from . import sale


def pre_init_hook(cr):
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'product_uom_price'")
    if cr.fetchall():
        migrate_from_product_uom_prices(cr)


def migrate_from_product_uom_prices(cr):
    # we need to rename table, sequence for next id and name on models table
    cr.execute('ALTER TABLE product_uom_price RENAME TO product_sale_uom')
    cr.execute('ALTER TABLE product_uom_price_id_seq RENAME TO product_sale_uom_id_seq')
    cr.execute("UPDATE ir_model_data SET model='product.sale.uom' "
               "WHERE model='product.uom.price'")
