{
    'name': 'Real Estate Management',
    'version': "16.0.1.0.0",
    'category': 'Localization/Argentina',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'summary': 'Training app',
    'depends': ['base'],
    'application': True,
    'data' : [
        'security/ir.model.access.csv',
        'views/real_estate_property_views.xml',
        'views/real_estate_property_type_views.xml',
        'views/real_estate_property_offer_views.xml',
        'views/real_estate_menus.xml',
    ],
}