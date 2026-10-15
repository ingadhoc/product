{
    "name": "Stock Account - Cost Change Revaluation",
    "version": "20.0.1.0.0",
    "author": "ADHOC SA",
    "license": "AGPL-3",
    "category": "Inventory/Accounting",
    "summary": "Posts the inventory revaluation entry when the accounting cost "
    "(standard_price) of a product with perpetual valuation (real_time) and "
    "standard or average (AVCO) costing changes.",
    "depends": ["stock_account"],
    "data": [
        "views/product_category_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
