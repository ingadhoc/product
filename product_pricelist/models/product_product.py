##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pricelist_ids = fields.One2many(
        'product.pricelist',
        compute='_compute_pricelist_ids',
        string='Pricelists',
    )

    def _compute_pricelist_ids(self):
        for rec in self:
            rec.pricelist_ids = rec.pricelist_ids.search([('show_products', '=', True)])
            rec.pricelist_ids.with_context(pricelist_product_id=rec.id)._compute_price()
