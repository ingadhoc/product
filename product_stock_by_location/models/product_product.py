##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def view_stock_detail(self):
        self.ensure_one()
        view = (
            'product_stock_by_location.view_product_stock_by_location_form')
        return {
            'name': _('Stock By Locations'),
            'target': 'new',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'view_id': self.env.ref(view).id,
            'type': 'ir.actions.act_window',
        }
