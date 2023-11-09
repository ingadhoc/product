# Real estate module for Adhoc developments by awe
{
    'name': 'Real Estate',
    'version': '13.0.1.0.0',
    'category': '',
    'sequence': 15,
    'summary': 'estate',
    'description': "",
    'website': 'https://www.adhoc.com.ar/',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
