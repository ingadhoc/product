{
    "name": "Bienes Raíces",  # name of the module
    "version": "19.0.1.0.0",  # version of the module
    "author": "ADHOC SA",  # author of the module
    "license": "AGPL-3",  # license of the module
    "depends": ["base"],  # dependency on the base module
    "application": True,  # this module is an application
    "data": [
        "security/ir.model.access.csv",  # access control list
        "views/estate_property_views.xml",  # views for estate properties
        "views/estate_property_type_views.xml",  # views for estate property types
        "views/estate_property_tag_views.xml",  # views for estate property tags
        "views/estate_property_offer_views.xml",  # views for estate property offers
        "views/estate_property_menus.xml",  # menu items for estate properties
    ],
}
