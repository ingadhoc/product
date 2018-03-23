##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo import exceptions
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp


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
        copy=True,
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

    # no-op for testing and calculating rule
    product_id = fields.Many2one(
        'product.template',
        'Test Product',
        compute=lambda x: x,
        inverse=lambda x: x,
    )

    demo_cost = fields.Float('Cost', compute=lambda x: x)
    demo_result = fields.Float('Result', compute=lambda x: x)

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
        # handle id instead of records
        if not obj and self.env.context.get('active_id') \
                and self.env.context.get('active_model') == 'product.template':
            obj = model.browse(self.env.context['active_id'])

        return {
            'env': env,
            'model': model,
            'Warning': exceptions.Warning,
            'product': obj,
        }

    def compute_rule(self, cost, product=None):
        # prepare context only if we need to eval something
        values = {}
        if any([l.expr for l in self.item_ids]):
            eval_context = self._get_eval_context(product)
            eval_context.update({
                'cost': cost,
                'lines': values,
            })

        for line in self.item_ids:
            error = False
            value = cost * (line.percentage_amount / 100.0) + line.fixed_amount
            # line expressions
            if line.expr:
                try:
                    eval_context.update({'cost_sum': cost})
                    res = safe_eval(str(line.expr), eval_context)
                    if isinstance(res, (int, float)):
                        value = value + res
                except Exception as e:
                    error = str(e)
                    pass

            values[line.name] = error or value
            line.value = error or str(value)
            if line.add_to_cost:
                cost = cost + value
        return cost

    @api.onchange('product_id', 'item_ids')
    def _onchange_product_id(self):
        """ On change to show dynamic results. """
        if self.product_id:
            cost = self.product_id.replenishment_base_cost_on_currency
            self.demo_cost = cost
            self.demo_result = self.compute_rule(cost, self.product_id)


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
        help='Specify the fixed amount to add or substract (if negative) to '
             'the amount calculated with the percentage amount.',
        digits=dp.get_precision('Product Price'),
    )

    expr = fields.Char(
        'Expression Amount',
        help='Specify a python expression that returns a float amount.\r\n'
             'You van use python variables:\r\n'
             '- env, model, Warning\r\n'
             '- product: the current product\r\n'
             '- cost: the base cost\r\n'
             '- cost_sum: the accumulated cost so far\r\n'
             '- lines: previous calculated lines (ie lines.get("line_name")',
    )

    add_to_cost = fields.Boolean(
        'Add to Cost',
        help='If true, this line value will be added to the cost. '
             'If not, it\'s just a variable.',
        default=True,
    )

    # no-op for testing and calculating rule
    value = fields.Char(
        compute=lambda x: x,
    )
