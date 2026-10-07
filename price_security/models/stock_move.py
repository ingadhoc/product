##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models

# since 19.0 the inventory valuation lives on the move instead of
# stock.valuation.layer: the value itself, the unit price it was valued at, and
# the texts that describe how it was computed, which spell the amounts out. The
# "in currency" ones come from stock_currency_valuation, which we do not depend
# on: listing a field that does not exist is harmless
COST_FIELDS = (
    "value",
    "remaining_value",
    "value_manual",
    "standard_price",
    "price_unit",
    "value_justification",
    "value_computed_justification",
    "value_in_currency",
    "value_manual_in_currency",
    "standard_price_in_currency",
)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "price.security.cost.mixin"]

    _price_security_cost_fields = COST_FIELDS
