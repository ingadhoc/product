##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    # name it _lst_price and not list_price because on product.product
    # we want to extend prices for lst_price (on product template list_price
    # and lst_price are the same)
    taxed_lst_price = fields.Float(
        string='Taxed Sale Price',
        compute='_compute_taxed_lst_price',
        digits=dp.get_precision('Product Price'),
    )

    @api.depends('taxes_id', 'list_price')
    def _compute_taxed_lst_price(self):
        """ compute it from list_price and not for lst_price for performance
        (avoid using dummy related field)
        """
        company_id = self._context.get(
            'company_id', self.env.user.company_id.id)
        for product in self:
            product.taxed_lst_price = product.taxes_id.filtered(
                lambda x: x.company_id.id == company_id).compute_all(
                    product.list_price,
                    self.env.user.company_id.currency_id,
                    product=product)['total_included']
