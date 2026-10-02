##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models

# inventory valuation columns on the quant lists: "value" from stock_account and
# "secondary_value" from stock_currency_valuation (not a dependency, the tuple is
# harmless when that module is not installed)
COST_FIELDS = ("value", "secondary_value")


class StockQuant(models.Model):
    _name = "stock.quant"
    _inherit = ["stock.quant", "price.security.cost.mixin"]

    _price_security_cost_fields = COST_FIELDS
