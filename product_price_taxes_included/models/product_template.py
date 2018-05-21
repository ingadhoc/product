##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # we do this so that we can show prices with or without taxe without
    # needing a pricelist
    @api.multi
    def _product_lst_price(self):
        # res = {}
        context = self._context
        company_id = (
            context.get('company_id') or self.env.user.company_id.id)
        taxes_included = context.get('taxes_included')

        for product in self:
            lst_price = product.list_price
            if taxes_included:
                lst_price = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                        lst_price, product=product)['total_included']
            product.lst_price = lst_price

    @api.model
    def _search_products_by_lst_price(self, operator, value):
        # TODO improove this, for now, at least we return products without
        # considering taxes
        return [('list_price', operator, value)]

    lst_price = fields.Float(
        compute='_product_lst_price',
        search='_search_products_by_lst_price',
        string='Public Price',
        # readonly=True,
        digits=dp.get_precision('Product Price')
    )

    taxed_lst_price = fields.Float(
        string='Taxed Sale Price',
        compute='get_taxed_lst_price',
        digits=dp.get_precision('Product Price'),
    )

    @api.multi
    @api.depends('taxes_id', 'lst_price')
    def get_taxed_lst_price(self):
        company_id = (
            self._context.get('company_id') or
            self.env.user.company_id.id)
        taxes_included = self._context.get('taxes_included')
        for product in self:
            # if taxes_included lst_price already has taxes included
            if taxes_included:
                product.taxed_lst_price = product.lst_price
            else:
                product.taxed_lst_price = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                        product.lst_price,
                        self.env.user.company_id.currency_id,
                        product=product)['total_included']
