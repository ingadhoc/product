# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_modify_prices = fields.Boolean(
        help='If checked all users can modify the\
        price of this product in a sale order or invoice.',
        string='Can modify prices')


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    sequence = fields.Integer(
        string='Sequence')
