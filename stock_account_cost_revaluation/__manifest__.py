{
    "name": "Stock Account - Cost Change Revaluation",
    "version": "19.0.1.0.0",
    "author": "ADHOC SA",
    "license": "AGPL-3",
    "category": "Inventory/Accounting",
    "summary": "Postea el asiento de revaluación de inventario al cambiar el costo "
    "contable (standard_price) de productos con categoría de valoración perpetua "
    "(real_time), en costeo estándar o promedio (AVCO).",
    "depends": [
        # ``product.value.account_move_id``, the field this module writes the
        # revaluation entry into. It is ``auto_install`` over ``stock_account``, so
        # declaring it costs nothing and makes the field guaranteed.
        "stock_account_ux",
    ],
    "data": [
        "views/product_category_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
