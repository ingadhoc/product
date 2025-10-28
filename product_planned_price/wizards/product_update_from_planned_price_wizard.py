##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, _
from odoo.exceptions import ValidationError


class ProductUpdateFromPlannedPriceWizard(models.TransientModel):
    _name = 'product.update_from_planned_price.wizard'
    _description = 'Update product price from planned price'

    def confirm(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if active_model != 'product.template':
            raise ValidationError(_(
                'Update from planned price must be called from product template'))
        products = self.env[active_model].browse(active_ids)
        # Hacemos esto para forzar el recomputo antes de llamar la metodo, presumimos que tiene que ver con los depends del _compute_computed_list_price Pero no lo queremos tocar en v16 
        for prod in products:
            prod.with_context(silent_compute=True)._compute_computed_list_price()
        products._update_prices_from_planned()
