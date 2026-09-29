##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models

# Value Adjustments (Inventory > Reporting), the report of the ticket. Besides
# the value itself go everything derived from it: the delta and the previous
# value that stock_account_ux adds, the texts describing how the value was
# computed, and the secondary currency twins from stock_currency_valuation.
# Neither module is a dependency: listing a field that does not exist is
# harmless
COST_FIELDS = (
    "value",
    "current_value",
    "current_value_details",
    "current_value_description",
    "computed_value_description",
    "previous_value",
    "delta",
    "value_in_currency",
    "previous_value_in_currency",
    "delta_in_currency",
)


class ProductValue(models.Model):
    _name = "product.value"
    _inherit = ["product.value", "price.security.cost.mixin"]

    _price_security_cost_fields = COST_FIELDS
