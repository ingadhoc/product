##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models

# since 19.0 the inventory valuation lives on the move instead of
# stock.valuation.layer
COST_FIELDS = ("value", "remaining_value", "value_manual", "standard_price")


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "price.security.cost.mixin"]

    _price_security_cost_fields = COST_FIELDS
