# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import openerp.addons.decimal_precision as dp


class ProductComputedListPriceRule(models.Model):
    _name = 'product.computed_list_price.rule'

    name = fields.Char(
        'Name',
        required=True,
    )
    item_ids = fields.One2many(
        'product.computed_list_price.rule.item',
        'computed_list_price_rule_id',
        'Items',
    )
    product_ids = fields.One2many(
        'product.template',
        'computed_list_price_rule_id',
        'Products',
    )


class ProductComputedListPriceRuleItem(models.Model):
    _name = 'product.computed_list_price.rule.item'
    _description = 'product.computed_list_price.rule.item'
    _order = 'sequence'

    computed_list_price_rule_id = fields.Many2one(
        'product.computed_list_price.rule',
        'Rule',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Char(
        'sequence',
        default=10,
    )
    name = fields.Char(
        'Name',
        required=True,
    )
    percentage_amount = fields.Float(
        'Percentage Amount',
        digits=dp.get_precision('Discount'),
    )
    fixed_amount = fields.Float(
        'Fixed Amount',
        digits=dp.get_precision('Product Price'),
        help='Specify the fixed amount to add or substract(if negative) to the'
        ' amount calculated with the percentage amount.'
    )
