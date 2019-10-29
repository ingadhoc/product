{
    'name': 'Integration between Replenishment Cost and Manufacture',
    'version': '11.0.1.5.0',
    'author': "ADHOC SA, Camptocamp,GRAP,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Products',
    'depends': [
        'product_replenishment_cost',
        'mrp',
    ],
    'website': 'http://www.camptocamp.com/',
    'data': [
        'report/mrp_bom_replenishment_cost_report_templates.xml',
    ],
    'installable': False,
}
