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
    'name': 'Product Computed List Price',
    'version': '8.0.0.1.1',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'description': """
Product Computed List Price
===========================
Errores conocidos:
Hay un bug de odoo por defecto que si agregas un producto en una sale order,
usas una unidad distinta a la del producto y abris el producto, el precio
que te muestra es según la unidad en la orden de venta y no según la unidad que
estás viendo del producto.
Una alternativa sería hacer lst_price readonly para que no pase este error en
la vista form de productos, esto se podría mejorar
    """,
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'product',
    ],
    'data': [
        'product_view.xml',
        'data.xml',
             ],
    'demo': [
        'demo/product_demo.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
