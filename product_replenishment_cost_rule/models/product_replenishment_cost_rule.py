# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from openerp import exceptions
from openerp.tools.safe_eval import safe_eval
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
        auto_join=True,
    )
    product_ids = fields.One2many(
        'product.template',
        'replenishment_cost_rule_id',
        'Products',
        auto_join=True,
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
                lambda x: "%s %s + %s%s" % (
                    x.name,
                    x.percentage_amount,
                    x.fixed_amount,
                    '+ expr' if x.expr else ''))))
        self.description = description

    @api.one
    @api.constrains('item_ids')
    def update_replenishment_cost_last_update(self):
        self.product_ids.update_replenishment_cost_last_update()

    def _get_eval_context(self, obj=None):
        """ Prepare the context used when evaluating python code
        :param obj: the current obj
        :returns: dict -- evaluation context given to (safe_)eval """
        env = api.Environment(self.env.cr, self.env.uid, self.env.context)
        model = env['product.template']
        obj_pool = self.pool['product.template']

        if not obj:
            if context.get('active_model') == 'product.template' and context.get('active_id'):
                obj = model.browse(context['active_id'])

        eval_context = {
            # orm
            'env': env,
            'model': model,
            # Exceptions
            'Warning': exceptions.Warning,
            # record
            'product': obj,
        }
        return eval_context

    def compute_rule(self, cost, product=None):
        values = {}
        if any([l.expr for l in self.item_ids]):
            eval_context = self._get_eval_context(product)
            eval_context.update({'lines': values})
        for line in self.item_ids:
            value = cost * \
                (line.percentage_amount / 100.0) \
                + line.fixed_amount
            # line expressions
            if line.expr:
                try:
                    res = safe_eval(str(line.expr), eval_context)
                    if isinstance(res, (int, float)):
                        value = value + res
                except:
                    # TODO: show error msg somewhere!
                    pass
            values[line.name] = value
            if line.add_to_cost:
                cost = cost + value
        return cost


class ProductReplenishmentCostRuleItem(models.Model):
    _name = 'product.replenishment_cost.rule.item'
    _description = 'product.replenishment_cost.rule.item'
    _order = 'sequence'

    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
        'Rule',
        required=True,
        ondelete='cascade',
        auto_join=True,
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
    expr = fields.Char('Expression Amount',
        help='Specify a python expression that returns a float amount.')

    add_to_cost = fields.Boolean('Add to Cost', default=True,
        help='If true, this line value will be added to the cost. '
             'If not, it\'s just a variable.')
