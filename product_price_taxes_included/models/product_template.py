##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def _product_lst_price(self):
        """ we do this so that we can show prices w/wo taxes without needing a
        pricelist
        """
        company_id = self._context.get(
            'company_id', self.env.user.company_id.id)
        taxes_included = self._context.get('taxes_included', False)

        for product in self:
            lst_price = product.list_price
            if taxes_included:
                lst_price = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                        lst_price, product=product)['total_included']
            product.lst_price = lst_price

    def _search_lst_price(self, operator, value):
        # TODO K. should be list_price or lst_price?
        products = self.env['product.product'].search(
            [('list_price', operator, value)], limit=None)
        return [('id', 'in', products.mapped('product_tmpl_id').ids)]

    lst_price = fields.Float(
        compute='_product_lst_price',
        search='_search_lst_price',
        string='Public Price',
        # readonly=True,
        digits=dp.get_precision('Product Price')
    )

    taxed_lst_price = fields.Float(
        string='Taxed Sale Price',
        compute='_compute_taxed_lst_price',
        digits=dp.get_precision('Product Price'),
    )

    @api.depends('taxes_id', 'lst_price')
    def _compute_taxed_lst_price(self):
        """ if taxes_included lst_price already has taxes included
        """
        company_id = self._context.get(
            'company_id', self.env.user.company_id.id)
        taxes_included = self._context.get('taxes_included')

        for product in self:
            product.taxed_lst_price = \
                product.lst_price if taxes_included else \
                product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                        product.lst_price,
                        self.env.user.company_id.currency_id,
                        product=product)['total_included']
