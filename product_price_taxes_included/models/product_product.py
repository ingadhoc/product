##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductProduct(models.Model):

    _inherit = 'product.product'

    taxed_lst_price = fields.Float(
        string='Taxed Sale Price',
        compute='_compute_taxed_lst_price',
        digits='Product Price',
    )

    @api.depends('taxes_id', 'lst_price')
    @api.depends_context('company', 'company_id')
    def _compute_taxed_lst_price(self):
        """ if taxes_included lst_price already has taxes included
        """
        company_id = self._context.get(
            'company_id', self.env.company.id)
        for product in self:
            product.taxed_lst_price = product.taxes_id.filtered(
                lambda x: x.company_id.id == company_id).sudo().compute_all(
                    product.lst_price,
                    self.env.company.currency_id,
                    product=product)['total_included']
