##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.tools import float_is_zero
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    computed_list_price_manual = fields.Float(
        string='Planned Price Manual',
        digits='Product Price',
        help='Field to store manual planned price',
    )
    computed_list_price = fields.Float(
        string='Planned Price',
        compute='_compute_computed_list_price',
        digits='Product Price',
        help='Planned Price. This value depends on Planned Price Type" an '
        'other parameters.',
    )
    list_price_type = fields.Selection([
        ('manual', 'Fixed value'),
        ('by_margin', 'By Margin'),
        ('other_currency', 'Currency exchange')
    ],
        string='Planned Price Type',
        # we make it optional
        # required=True,
        default='manual',
        help="If the 'Fixed value' type is chosen, a fixed planned"
        " price is defined. \n If the 'By margin' type is chosen, "
        "the following formula will be taken into account for "
        "the planned price: Replenishment cost * (1 + margin(%)) + surcharge."
        "\n If the 'Currency exchange' type is chosen, The planned price is "
        "set in the chosen currency and converted to the product's currency",
    )
    sale_margin = fields.Float(
        'Planned Price Sale margin %',
        digits='Discount',
    )
    sale_surcharge = fields.Float(
        'Planned Price Sale surcharge',
        digits='Product Price',
    )
    other_currency_id = fields.Many2one(
        'res.currency',
        'Planned Currency',
        help="Currency used for the Currency List Price.",
    )
    other_currency_list_price = fields.Float(
        'Planned Price on Currency',
        digits='Product Price',
        help="Sale Price on Other Currency",
    )

    @api.model
    def cron_update_prices_from_planned(self):
        _logger.info('Running update prices from planned cron')
        if self._context.get('force_company'):
            self = self.with_company(self._context.get('force_company'))
        else:
            self = self.with_company(self.env['res.company'].search([], limit=1).id)
        
        return self.with_context(bypass_base_automation=True)._update_prices_from_planned()

    def _update_prices_from_planned(self):
        """
        If we came from tree list, we update only in selected list
        Despues de varias pruebas, obtuvimos la mejor pefromance de esta manera
        Haciendo practicamente lo de ahora pero sin el slice tuvimos une
        performance basatante peor (casi 2 o 3 veces mas de tiempo)
        """
        prec = self.env['decimal.precision'].precision_get('Product Price')

        # we search again if it is called from list view
        domain = [('list_price_type', '!=', False)]
        if self:
            domain.append(('id', 'in', self.ids))

        cr = self._cr
        for rec in self.with_context(
                prefetch_fields=False).search(domain).filtered(
                lambda x: x.computed_list_price and not float_is_zero(
                    x.computed_list_price - x.list_price,
                    precision_digits=prec)):
            # es mucho mas rapido hacerlo por sql directo
            cr.execute(
                "UPDATE product_template SET list_price=%s WHERE id=%s",
                (rec.computed_list_price or 0.0, rec.id))
        return True

    @api.depends(
        'sale_margin',
        'sale_surcharge',
        'replenishment_cost',
        'list_price_type',
        'computed_list_price_manual',
        'other_currency_list_price',
        'other_currency_id',
    )
    @api.depends_context('company')
    def _compute_computed_list_price(self):
        recs = self.filtered(
            lambda x: x.list_price_type in [
                'manual', 'by_margin', 'other_currency'])
        _logger.info('Get computed_list_price for %s "manual", "by_margin"'
                     ' and "other_currency" products' % (len(recs)))
        company = self.env.company
        date = fields.Date.today()
        (self - recs).computed_list_price = 0.0
        for rec in recs:
            computed_list_price = rec.computed_list_price_manual
            if rec.list_price_type == 'by_margin':
                computed_list_price = rec.replenishment_cost * \
                    (1 + rec.sale_margin / 100.0) + rec.sale_surcharge
            elif rec.list_price_type == 'other_currency' and rec.currency_id:
                computed_list_price = rec.other_currency_id._convert(
                    rec.other_currency_list_price,
                    rec.currency_id, company, date, round=False)

            # if product has taxes with price_include, add the tax to the
            # sale price
            inc_taxes = rec.taxes_id.filtered('price_include')
            if inc_taxes:
                computed_list_price = inc_taxes.compute_all(
                    computed_list_price, rec.currency_id,
                    product=rec, handle_price_include=False)['total_included']

            rec.update({
                'computed_list_price': computed_list_price,
            })

    def price_compute(
            self, price_type, uom=False, currency=False, company=False, date=False):
        """
        We do this so that if someone wants to force the calculated price
        be based on the planned, you can do it by sending use_planned_price
        in the context
        """
        if self._context.get(
                'use_planned_price') and price_type == 'list_price':
            price_type = 'computed_list_price'
        return super().price_compute(price_type, uom=uom, currency=currency, company=company, date=date)
