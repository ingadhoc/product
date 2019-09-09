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
    'name': 'Product Catalog Aeroo Report',
    'version': '12.0.1.0.0',
    'category': 'Aeroo Reporting',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'product_price_taxes_included',
        'report_aeroo',
        'sale',
        'stock',
    ],
    'data': [
        'wizards/product_catalog_wizard_views.xml',
        'security/ir.model.access.csv',
        'views/product_catalog_report_views.xml',
        'report/product_catalog_report_data.xml'
    ],
    'demo': [
        'demo/product_template_demo.xml',
        'demo/product_product_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
