{
    "name": "Replenishment Cost",
<<<<<<< d6638e16365b2c5ed6b3ffbefd1e928e4da7cf7f
    "version": "19.0.1.4.0",
||||||| fca4cd7719ef9bd5dcd02d5628cd0cd41756906c
    "version": "19.0.1.5.0",
=======
    "version": "19.0.1.6.0",
>>>>>>> 374f5573098a76bef0ee1c2dd0a3164c857e9bc3
    "author": "ADHOC SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Products",
    "depends": [
        "purchase",  # for page in product form
        "sales_team",  # for access rights
        "sale",  # only for menu for cost rules
    ],
    "data": [
        "security/product_replenishment_cost_security.xml",
        "data/ir_cron_data.xml",
        "views/product_template_views.xml",
        "views/product_replenishment_cost_rule_views.xml",
        "views/product_supplierinfo_views.xml",
        "wizards/product_update_from_replenishment_cost_wizard_views.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/replenishment_cost_demo.xml",
    ],
    "installable": False,
}
