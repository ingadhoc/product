{
    'name': 'Product Attribute Template',
    'version': "18.0.1.0.0",
    'category': 'Sales Management',
    'author': 'ADHOC SA, Odoo Community Association (OCA)',
    'website': 'http://www.adhoc.com.ar/',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_attribute_template_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
}
