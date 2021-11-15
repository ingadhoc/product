{
    'name': 'Replenishment Cost',
    'version': "15.0.1.0.0",
    'author': "ADHOC SA, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Products',
    'depends': [
        # for use the user company currency for the standard price
        'product_ux',
        # for page in product form
        'purchase',
        # for access rights
        'sales_team',
        # only for menu for cost rules
        'sale',
    ],
    'data': [
        'security/product_replenishment_cost_security.xml',
        'data/ir_cron_data.xml',
        'views/product_template_views.xml',
        'views/product_replenishment_cost_rule_views.xml',
        'views/product_supplierinfo_views.xml',
        'wizards/product_update_from_replenishment_cost_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
