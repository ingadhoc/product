# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    computed_list_price_manual = fields.Float(
        string='Planned Price Manual',
        help='Field to store manual planned price'
    )
    computed_list_price = fields.Float(
        string='Planned Price',
        compute='_get_computed_list_price',
        help='Planned Price. This value depends on Planned Price Type" an '
        'other parameters.',
    )
    list_price_type = fields.Selection([
        ('manual', 'Fixed value')],
        string='Planned Price Type',
        # we make it optional
        # required=True,
        default='manual',
    )

    @api.model
    def cron_update_prices_from_planned(self, limit=None):
        _logger.info('Running update prices from planned cron')
        # batch_size = 1000
        # product_ids = self.search([('list_price_type', '!=', False)]).ids
        # sliced_product_ids = [
        #     product_ids[i:i + batch_size] for i in range(
        #         0, len(product_ids), batch_size)]
        # for product_ids in sliced_product_ids:
        #     self.browse(product_ids)._update_prices_from_planned()
        # # for product in self.search(
        # #         [('list_price_type', '!=', False)], limit=limit):
        # #     product._update_prices_from_planned()
        # #     self._cr.commit()
        # return True
        return self.search(
            [('list_price_type', '!=', False)])._update_prices_from_planned()

    @api.multi
    def _update_prices_from_planned(self):
        for rec in self:
            if not rec.list_price_type:
                continue
            rec.list_price = rec.computed_list_price
        return True

    @api.multi
    @api.depends(
        'list_price_type',
        'computed_list_price_manual',
    )
    def _get_computed_list_price(self):
        _logger.info('Getting Compute List Price for products: "%s"' % (
            self.ids))
        for template in self:
            print 'template', template
            if not template.list_price_type:
                continue
            computed_list_price = template.get_computed_list_price()
            computed_list_price = template._other_computed_rules(
                computed_list_price)
            template.computed_list_price = computed_list_price

    @api.multi
    def _other_computed_rules(self, computed_list_price):
        self.ensure_one()
        return computed_list_price

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        return self.computed_list_price_manual
