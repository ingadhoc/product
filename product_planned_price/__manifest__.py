##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Product Planned Price',
    'version': '12.0.1.1.0',
    'category': 'Product',
    'sequence': 14,
    'author': 'ADHOC SA,Odoo Community Association (OCA)',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'product_replenishment_cost',
    ],
    'data': [
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'wizards/product_update_from_planned_price_wizard_views.xml',
        'data/ir_cron_data.xml',
        'security/product_planned_price_security.xml',
    ],
    'demo': [
        'demo/product_product_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
