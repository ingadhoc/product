##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    @api.constrains('value_ids', 'attribute_id')
    def _check_valid_attribute(self):
        # We do this to avoid the constrains when you try to generarate attributes by the button in product attribute
        # template, that it's only to initialize attribute then the user add values to this
        if self._context.get('non_create_values', False) and any(
                line.value_ids > line.attribute_id.value_ids for line in self):
            raise ValidationError(_('You cannot use this attribute with the following value.'))
        elif not self._context.get('non_create_values', False):
            super()._check_valid_attribute()
        return True
