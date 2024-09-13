# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Real Estate Managment',
    'version': "16.0.1.0.0",
    'author': 'ADHOC SA, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['base'],
    'application' : True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',         
        'views/estate_property_offer_views.xml', 
        'views/res_users_views.xml',  
        'views/estate_menus.xml',
    ]
}
