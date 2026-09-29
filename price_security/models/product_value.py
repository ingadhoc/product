##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models

COST_FIELDS = ("value", "current_value")


class ProductValue(models.Model):
    _name = "product.value"
    _inherit = ["product.value", "price.security.cost.mixin"]

    _price_security_cost_fields = COST_FIELDS
