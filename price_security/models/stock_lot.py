##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models

# inventory valuation fields added by stock_account on the lot form
COST_FIELDS = ("total_value", "avg_cost", "standard_price")


class StockLot(models.Model):
    _name = "stock.lot"
    _inherit = ["stock.lot", "price.security.cost.mixin"]

    _price_security_cost_fields = COST_FIELDS
