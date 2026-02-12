##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    @api.onchange("attribute_id")
    def _onchange_attribute_id(self):
        # Same behavior for all attribute types: do not auto-select values
        self.value_ids = self.value_ids.filtered(lambda pav: pav.attribute_id == self.attribute_id)
