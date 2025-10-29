##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    @api.constrains("active", "value_ids", "attribute_id")
    def _check_valid_values(self):
        # We do this to avoid the constrains when you try to generarate attributes by the button in product attribute
        # template, that it's only to initialize attribute then the user add values to this
        if self.env.context.get("non_create_values", False):
            return True
        super()._check_valid_values()
