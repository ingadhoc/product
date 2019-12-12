{
    'name': 'Integration between Replenishment Cost and Manufacture',
    'version': '12.0.1.0.0',
    'author': "ADHOC SA, Camptocamp, GRAP, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Products',
    'depends': [
        'product_replenishment_cost',
        'mrp',
    ],
    'website': 'http://www.camptocamp.com/',
    'data': [
        'views/mrp_bom_views.xml',
        'report/mrp_report_bom_structure.xml'
    ],
    'installable': True,
}
