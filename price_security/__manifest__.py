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
    'name': 'Price Security',
    'version': '11.0.1.0.0',
    'category': 'Sales Management',
    'author': 'ADHOC SA, Odoo Community Association (OCA)',
    'website': 'http://www.adhoc.com.ar/',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/invoice_views.xml',
        'views/partner_views.xml',
        'views/account_views.xml',
    ],
    'installable': True,
}
