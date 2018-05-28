##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # product_id = fields.Integer(
    #     related='product_variant_ids.product_id'
    #     # 'product.pricelist',
    #     # compute='_get_product_id',
    #     # store=True
    #     )
    # pricelist_ids = fields.Many2many(
    pricelist_ids = fields.One2many(
        'product.pricelist',
        compute='_compute_pricelist_ids',
        # inverse='dummy_inverse',
        string='Pricelists',
    )

    # not implemented yet
    # @api.one
    # def dummy_inverse(self):
    #     return True

    @api.multi
    def _compute_pricelist_ids(self):
        for rec in self:
            self.pricelist_ids = self.pricelist_ids.search(
                [('show_products', '=', True)])
