# -*- coding: utf-8 -*-
# Copyright 2009 Àngel Àlvarez - NaN  (http://www.nan-tic.com)
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product Pack',
    'version': '10.0.1.0.0',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'author': 'NaN·tic, ADHOC SA, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pack_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
