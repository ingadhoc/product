##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, _
from odoo.exceptions import UserError


class ProductUpdateFromReplenishmentCostWizard(models.TransientModel):
    _name = 'product.update_from_replenishment_cost.wizard'
    _description = 'Update product cost from replenishment cost'

    @api.multi
    def confirm(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if active_model != 'product.template':
            raise UserError(_(
                'Update from replenishment cost must be called from product '
                'template'))
        return self.env[active_model].browse(
            active_ids)._update_cost_from_replenishment_cost()
