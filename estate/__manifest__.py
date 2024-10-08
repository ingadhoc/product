{
    'name' : 'Real Estate Management',
    'depends': ['base'],
    'application' :True,
    'description' : 'Modulo test para la induccion a sistemas Adhoc',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_user_views.xml',
        'views/estate_menu.xml',        
    ],
}