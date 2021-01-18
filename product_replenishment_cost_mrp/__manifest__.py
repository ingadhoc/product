{
    'name': 'Integration between Replenishment Cost and Manufacture',
    'version': '13.0.1.0.0',
    'author': "ADHOC SA, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Products',
    'depends': [
        'product_replenishment_cost',
        'mrp',
    ],
    'data': [
        'views/mrp_bom_views.xml',
        'report/mrp_report_bom_structure.xml'
    ],
    'installable': True,
}
