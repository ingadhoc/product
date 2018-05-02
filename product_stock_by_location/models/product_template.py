##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    location_ids = fields.One2many(
        'stock.location',
        compute='_compute_location_ids',
        string='Locations',
    )

    @api.multi
    # dummy depends it is computed
    @api.depends('name')
    def _compute_location_ids(self):
        for rec in self:
            rec.location_ids = rec.location_ids.search([
                ('show_stock_on_products', '=', True)])

    @api.multi
    def view_stock_detail(self):
        self.ensure_one()
        view = (
            'product_stock_by_location.view_template_stock_by_location_form')
        return {
            'name': _('Stock By Locations'),
            'target': 'new',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'view_id': self.env.ref(view).id,
            'flags': {'initial_mode': 'view'},
            'type': 'ir.actions.act_window'
        }
