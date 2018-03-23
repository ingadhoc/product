##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    list_price_type = fields.Selection(
        selection_add=[('other_currency', 'Currency exchange')],
    )
    other_currency_id = fields.Many2one(
        'res.currency',
        'Planned Currency',
        # help="Currency used for the Currency List Price.",
    )
    other_currency_list_price = fields.Float(
        'Planned Price on Currency',
        digits=dp.get_precision('Product Price'),
        # help="Sale Price on Other Currency",
    )

    @api.multi
    @api.depends(
        'other_currency_list_price',
        'other_currency_id',
    )
    def _get_computed_list_price(self):
        other_currency_recs = self.filtered(
            lambda x: x.list_price_type == 'other_currency' and
            x.other_currency_id)
        _logger.info(
            'Get computed_list_price for %s "other_currency" products' % (
                len(other_currency_recs)))
        # el campo calculado currency_id no se computa hasta guardar
        for rec in other_currency_recs.filtered('currency_id'):
            rec.computed_list_price = rec.other_currency_id.compute(
                rec.other_currency_list_price,
                rec.currency_id,
                round=False)
        other_type_recs = self - other_currency_recs
        return super(
            ProductTemplate, other_type_recs)._get_computed_list_price()
