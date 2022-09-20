{
    'name': 'Real Estate Management',
    'depends': ['base'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_types_view.xml',
        'views/estate_property_tag_view.xml',
        'views/estate_property_offer.xml',
        'views/estate_menus.xml',
    ]
}