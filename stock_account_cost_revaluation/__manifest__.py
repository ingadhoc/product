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
        "stock_account",
    ],
    "data": [
        "views/product_category_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
