##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.depends('list_price', 'price_extra')
    def _compute_product_lst_price(self):
        """ We do this so that we can show prices w/wo taxes without needing a
        pricelist
        """
        super(ProductProduct, self)._compute_product_lst_price()
        if not self._context.get('taxes_included', False):
            return

        company_id = self._context.get(
            'company_id', self.env.user.company_id.id)

        for product in self:
            product.lst_price = product.taxes_id.filtered(
                lambda x: x.company_id.id == company_id).compute_all(
                    product.lst_price, product=product.id)['total_included']

    def _set_product_lst_price(self):
        if self._context.get('taxes_included'):
            raise UserError(_(
                "You can not set list price if you are working with 'Taxes "
                "Included' in the context"))
        return super(ProductProduct, self)._set_product_lst_price()
