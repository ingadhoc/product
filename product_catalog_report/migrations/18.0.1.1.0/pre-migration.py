def migrate(cr, version):
    cr.execute(
        "UPDATE product_product_catalog_report "
        "SET category_type = 'product_category' "
        "WHERE category_type = 'accounting_category'"
    )
