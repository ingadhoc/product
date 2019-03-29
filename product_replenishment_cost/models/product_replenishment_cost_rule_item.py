##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
import odoo.addons.decimal_precision as dp


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

    sequence = fields.Integer(
        required=True,
        default=10,
    )

    name = fields.Char(
        required=True,
    )

    percentage_amount = fields.Float(
        digits=dp.get_precision('Discount'),
    )

    fixed_amount = fields.Float(
        help='Specify the fixed amount to add or substract (if negative) to '
             'the amount calculated with the percentage amount.',
        digits=dp.get_precision('Product Price'),
    )

    expr = fields.Char(
        'Expression Amount',
        help='Specify a python expression that returns a float amount.\n'
             'You van use python variables:\n'
             '- env, model, Warning\n'
             '- product: the current product\n'
             '- cost: the base cost\n'
             '- cost_sum: the accumulated cost so far\n'
             '- lines: previous calculated lines (ie lines.get("line_name")',
    )

    add_to_cost = fields.Boolean(
        help='If true, this line value will be added to the cost. '
             'If not, it\'s just a variable.',
        default=True,
    )

    # no-op for testing and calculating rule
    value = fields.Char(
        compute=lambda x: x,
        help="Technical fields: This field it's only for testing",
    )
    error = fields.Char(
        compute=lambda x: x,
        help="Technical fields: This field it's only for testing",
    )
