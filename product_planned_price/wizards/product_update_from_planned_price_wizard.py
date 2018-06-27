##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductUpdateFromPlannedPriceWizard(models.TransientModel):
    _name = 'product.update_from_planned_price.wizard'
    _description = 'Update product price from planned price'

    @api.multi
    def confirm(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if active_model != 'product.template':
            raise ValidationError(_(
                'Update from planned price must be called from product '
                'template'))
        return self.env[active_model].browse(
            active_ids)._update_prices_from_planned()
