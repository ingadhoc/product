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
    'name': 'Planned Price By Margin',
    'version': '9.0.1.0.0',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        # we make dependant on this module because it adds rep cost field
        # on prod template. TODO this mods should go to
        # product_replenishment_cost module
        'product_replenishment_cost_currency',
        # 'product_replenishment_cost',
        'product_computed_list_price',
    ],
    'data': ['product_view.xml'
             ],
    'demo': [
        'demo/product_demo.xml',
    ],
    'test': [
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
