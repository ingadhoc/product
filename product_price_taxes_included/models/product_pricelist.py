##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def get_products_price(
            self, products, quantities, partners, date=False, uom_id=False):
        """If we send taxes_included on context we include price on the
        requested prices for this pricelist. We do it here and not in
        price_compute of product.template / product.product because:
        * we only need to do it once
        * pricelist could be based on fixed prices so product price is not used
        """
        res = super().get_products_price(
            products, quantities, partners, date=date, uom_id=uom_id)
        if self._context.get('taxes_included'):
            company_id = (
                self._context.get('company_id') or self.env.user.company_id.id)
            for product in products:
                res[product.id] = product.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                        res[product.id], product=product.id)['total_included']
        return res
