{
    'name': 'Products Expiration Date UX',
    'version': "18.0.1.0.0",
    'category': 'Inventory/Inventory',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'depends': [
        'product_expiry',
        'stock_ux',
    ],
    'data': [
        'views/production_lot_views.xml',
        'views/stock_move_line_views.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
    'application': False,
}
