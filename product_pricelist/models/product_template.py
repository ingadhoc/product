##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pricelist_ids = fields.One2many(
        'product.pricelist',
        compute='_compute_pricelist_ids',
        string='Pricelists',
    )

    @api.multi
    def _compute_pricelist_ids(self):
        for rec in self:
            rec.pricelist_ids = rec.pricelist_ids.search(
                [('show_products', '=', True)])
