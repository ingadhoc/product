##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = "product.template"

    sale_margin = fields.Float(
        'Planned Price Sale margin %',
        digits=dp.get_precision('Discount'),
    )
    sale_surcharge = fields.Float(
        'Planned Price Sale surcharge',
        digits=dp.get_precision('Product Price')
    )
    list_price_type = fields.Selection(
        selection_add=[('by_margin', 'By Margin')],
    )
    replenishment_cost_copy = fields.Float(
        related='replenishment_cost'
        # related='product_variant_ids.replenishment_cost'
    )

    @api.multi
    @api.depends(
        'sale_margin',
        'sale_surcharge',
        'replenishment_cost',
    )
    def _get_computed_list_price(self):
        by_margin_recs = self.filtered(
            lambda x: x.list_price_type == 'by_margin')
        _logger.info('Get computed_list_price for %s "by_margin" products' % (
            len(by_margin_recs)))
        for rec in by_margin_recs:
            rec.computed_list_price = rec.replenishment_cost * \
                (1 + rec.sale_margin / 100.0) + rec.sale_surcharge
        other_type_recs = self - by_margin_recs
        return super(
            product_template, other_type_recs)._get_computed_list_price()
