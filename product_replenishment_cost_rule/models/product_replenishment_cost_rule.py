# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductReplenishmentCostRule(models.Model):
    _name = 'product.replenishment_cost.rule'
    _description = 'product.replenishment_cost.rule'
    _inherit = ['mail.thread']

    name = fields.Char(
        'Name',
        required=True,
    )
    item_ids = fields.One2many(
        'product.replenishment_cost.rule.item',
        'replenishment_cost_rule_id',
        'Items',
    )
    product_ids = fields.One2many(
        'product.template',
        'replenishment_cost_rule_id',
        'Products',
    )
    description = fields.Char(
        compute='_compute_description',
        store=True,
        track_visibility='onchange',
    )

    @api.one
    @api.depends(
        'name',
        'item_ids.name',
        'item_ids.percentage_amount',
        'item_ids.fixed_amount',
    )
    def _compute_description(self):
        # "asdasda: line name 40% + 12, line 2 13% + 2" % (
        description = "%s: %s" % (
            self.name,
            ', '.join(self.item_ids.mapped(
                lambda x: "%s %s + %s" % (
                    x.name, x.percentage_amount, x.fixed_amount))))
        self.description = description

    @api.one
    @api.constrains('item_ids')
    def update_replenishment_cost_last_update(self):
        self.product_ids.update_replenishment_cost_last_update()


class ProductReplenishmentCostRuleItem(models.Model):
    _name = 'product.replenishment_cost.rule.item'
    _description = 'product.replenishment_cost.rule.item'
    _order = 'sequence'

    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
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
