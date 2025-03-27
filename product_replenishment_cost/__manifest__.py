{
    "name": "Replenishment Cost",
    "version": "18.0.1.1.0",
    "author": "ADHOC SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Products",
    "depends": [
        "purchase",  # for page in product form
        "sales_team",  # for access rights
        "sale",  # only for menu for cost rules
        "account_multicompany_ux",  # for usability in multicompany environments
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
    "installable": True,
}
