# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class ProductPricelitt(models.Model):
    _inherit = "product.pricelist"

    # se hizo esto porque desde website_sale llama a price_rule_get_multi y
    # no _price_get_multi, entonces modificamos _price_rule_get_multi
    @api.model
    def _price_rule_get_multi(self, pricelist, products_by_qty_by_partner):
        # we send last_pricelist on the first call and then we add taxes only
        # if this is the last pricelist (this is due to an error with
        # pricelist recursive)
        if not self._context.get('last_pricelist'):
            self = self.with_context(last_pricelist=pricelist)
        res = super(ProductPricelitt, self)._price_rule_get_multi(
            pricelist, products_by_qty_by_partner)
        if (
                self._context.get('taxes_included') and
                self._context.get('last_pricelist') == pricelist):

            company_id = (
                self._context.get('company_id') or self.env.user.company_id.id)
            for product, qty, partner in products_by_qty_by_partner:
                if pricelist.type == 'purchase':
                    res[product.id] = (product.supplier_taxes_id.filtered(
                        lambda x: x.company_id.id == company_id).compute_all(
                        res[product.id][0], 1.0, product=product,
                        partner=partner)['total_included'], res[product.id][1])
                else:
                    res[product.id] = (product.taxes_id.filtered(
                        lambda x: x.company_id.id == company_id).compute_all(
                        res[product.id][0], 1.0, product=product,
                        partner=partner)['total_included'], res[product.id][1])
        return res
