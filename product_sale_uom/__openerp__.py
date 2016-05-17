# -*- coding: utf-8 -*-
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
    'name': 'Product Sale UOMS',
    'version': '8.0.0.3.0',
    'category': 'base.module_category_knowledge_management',
    'description': """
Product Sale UOMS
=================
* Add a o2m field on products to allow defining uoms that can be used on sale
orders
""",
    'author': 'ADHOC SA.',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'test': [],
    'demo': [
        'demo/product_demo.xml',
    ],
    'data': [
        'data.xml',
        'view/product_view.xml',
        'view/sale_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
