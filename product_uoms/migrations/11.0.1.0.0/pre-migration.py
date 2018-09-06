from openupgradelib import openupgrade


table_renames = [
    ('product_sale_uom', 'product_uoms'),
]

model_renames = [
    ('product.sale.uom', 'product.uoms'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_models(cr, model_renames)
