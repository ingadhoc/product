{
    "name": "Real Estate",  # The name that will appear in the App list
    "version": "16.0.1.0",  # Version
    "application": True,  # This line says the module is an App, and not a module
    "depends": ["base"],  # dependencies
    "data": [
        'security/ir.model.access.csv',
        'views/estate_property_menu.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tags_views.xml',
        'views/estate_property_offer_view.xml'
    ],
    "installable": True,
    'license': 'LGPL-3',
}
