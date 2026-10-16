##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import AccessError


class ProductReplenishmentCostRuleItem(models.Model):
    _name = "product.replenishment_cost.rule.item"
    _description = "product.replenishment_cost.rule.item"
    _order = "sequence"

    replenishment_cost_rule_id = fields.Many2one(
        "product.replenishment_cost.rule",
        "Rule",
        required=True,
        ondelete="cascade",
        bypass_search_access=True,
    )

    sequence = fields.Integer(
        required=True,
        default=10,
    )

    name = fields.Char(
        required=True,
    )

    percentage_amount = fields.Float(
        digits="Discount",
        help="Percentage applied over the cost accumulated up to this line.",
    )

    fixed_amount = fields.Float(
        help="Specify the fixed amount to add or substract (if negative) to "
        "the amount calculated with the percentage amount.",
        digits="Product Price",
    )

    expr = fields.Char(
        "Expression Amount",
        help="Specify a python expression that returns a float amount.\n"
        "You van use python variables:\n"
        "- env, model, Warning\n"
        "- product: the current product\n"
        "- cost: the base cost\n"
        "- cost_sum: the accumulated cost so far\n"
        '- lines: previous calculated lines (ie lines.get("line_name")',
    )

    add_to_cost = fields.Boolean(
        help="If true, this line value will be added to the cost. " "If not, it's just a variable.",
        default=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get("expr") for vals in vals_list):
            self._check_expr_access()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("expr"):
            self._check_expr_access()
        return super().write(vals)

    def _check_expr_access(self):
        """The expression runs as python code with the environment: only trusted users may set it."""
        if self.env.su or self.env.user.has_group("product_replenishment_cost.group_replenishment_rule_expr"):
            return
        raise AccessError(
            self.env._("Only users allowed to use expressions on replenishment cost rules can set an expression.")
        )
