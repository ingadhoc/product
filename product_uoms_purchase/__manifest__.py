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
    'name': 'Product UOMS Purchase',
    'version': "15.0.1.0.0",
    'category': 'base.module_category_knowledge_management',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'product_uoms',
        # TODO when migrate analyze if this depends are necessary or
        # we do the part of the "stock.rule" in a bridge module
        'purchase_stock',
    ],
    'demo': [
    ],
    'data': [
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
