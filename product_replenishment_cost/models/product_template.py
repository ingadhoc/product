##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.tools import float_compare
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier_currency_id = fields.Many2one(
        related='seller_ids.currency_id',
        string="Supplier Currency"
    )
    supplier_price = fields.Float(
        string='Supplier Price',
        related='seller_ids.net_price',
    )
    standard_price = fields.Float(
        string='Accounting Cost',
    )
    replenishment_cost = fields.Float(
        compute='_compute_replenishment_cost',
        # TODO, activamos store como estaba??
        store=False,
        digits=dp.get_precision('Product Price'),
        help="Replenishment cost on the currency of the product",
    )
    replenishment_cost_last_update = fields.Datetime(
        track_visibility='onchange',
    )
    replenishment_base_cost = fields.Float(
        digits=dp.get_precision('Product Price'),
        track_visibility='onchange',
        help="Replanishment Cost expressed in 'Replenishment Base Cost "
        "Currency'."
    )
    replenishment_base_cost_currency_id = fields.Many2one(
        'res.currency',
        'Replenishment Base Cost Currency',
        auto_join=True,
        track_visibility='onchange',
        help="Currency used for the Replanishment Base Cost.",
        default=lambda self: self.env.user.company_id.currency_id.id
    )
    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
        auto_join=True,
        index=True,
        track_visibility='onchange',
    )
    replenishment_base_cost_on_currency = fields.Float(
        compute='_compute_replenishment_cost',
        help='Replenishment cost on replenishment base cost currency',
        digits=dp.get_precision('Product Price'),
    )
    replenishment_cost_type = fields.Selection(
        [('supplier_price', 'Supplier Price'),
         ('manual', 'Manual')],
        default='manual',
        required=True,
    )

    @api.model
    def cron_update_cost_from_replenishment_cost(self, limit=None):
        _logger.info('Running cron update cost from replenishment')
        return self.with_context(
            commit_transaction=True)._update_cost_from_replenishment_cost()

    @api.multi
    def _update_cost_from_replenishment_cost(self):
        """
        If we came from tree list, we update only in selected list
        Actulizamos product.product ya que el standard_price esta en ese modelo
        """
        prec = self.env['decimal.precision'].precision_get('Product Price')

        domain = [
            '|', ('replenishment_cost_rule_id', '!=', False),
            '|', '&', ('seller_ids', '!=', False),
            ('replenishment_cost_type', '=', 'supplier_price'),
            '&', '&',
            ('replenishment_cost_type', '=', 'manual'),
            ('replenishment_base_cost', '!=', False),
            ('replenishment_base_cost_currency_id', '!=', False),
        ]
        if self:
            domain.append(('product_tmpl_id.id', 'in', self.ids))

        products = self.env['product.product'].with_context(
            prefetch_fields=False).search(domain)
        for product in products.filtered('replenishment_cost'):
            replenishment_cost = product.replenishment_cost
            if product.currency_id != product.user_company_currency_id:
                replenishment_cost = product.currency_id._convert(
                    replenishment_cost, product.user_company_currency_id,
                    product.company_id, fields.Date.today(),
                    round=False)
            if float_compare(
                    product.standard_price,
                    replenishment_cost,
                    precision_digits=prec) != 0:
                product.standard_price = replenishment_cost
        return True

    @api.constrains(
        'replenishment_base_cost',
        'replenishment_base_cost_currency_id',
    )
    def update_replenishment_cost_last_update(self):
        # con el tracking_disable nos ahorramos doble mensaje
        self.with_context(tracking_disable=True).write(
            {'replenishment_cost_last_update': fields.Datetime.now()})

    # TODO ver si necesitamos borrar estos depends o no, por ahora
    # no parecen afectar performance y sirvern para que la interfaz haga
    # el onchange, pero no son fundamentales porque el campo no lo storeamos
    @api.depends(
        'currency_id',
        'replenishment_cost_type',
        'replenishment_base_cost',
        # beccause field is not stored anymore we only keep currency and
        # rule
        'replenishment_base_cost_currency_id',
        # # because of being stored
        # 'replenishment_base_cost_currency_id.rate_ids.rate',
        # # and this if we change de date (name field)
        # 'replenishment_base_cost_currency_id.rate_ids.name',
        # rule items
        'replenishment_cost_rule_id',
        # 'replenishment_cost_rule_id.item_ids.sequence',
        # 'replenishment_cost_rule_id.item_ids.percentage_amount',
        # 'replenishment_cost_rule_id.item_ids.fixed_amount',
    )
    def _compute_replenishment_cost(self):
        _logger.info(
            'Getting replenishment cost for ids %s' % self.ids)
        company = self.env.user.company_id
        date = fields.Date.today()
        for rec in self:
            product_currency = rec.currency_id
            if rec.replenishment_cost_type == 'supplier_price':
                replenishment_base_cost = rec.supplier_price
                base_cost_currency = rec.supplier_currency_id
            elif rec.replenishment_cost_type == 'manual':
                replenishment_base_cost = rec.replenishment_base_cost
                base_cost_currency = rec.replenishment_base_cost_currency_id

            # we enforce a replenishment base cost currency to be configured
            if not base_cost_currency:
                continue

            replenishment_cost_rule = rec.replenishment_cost_rule_id
            replenishment_cost = base_cost_currency._convert(
                replenishment_base_cost, product_currency,
                company, date, round=False)

            replenishment_base_cost_on_currency = replenishment_cost
            if replenishment_cost_rule:
                replenishment_cost =\
                    replenishment_cost_rule.compute_rule(
                        replenishment_base_cost_on_currency, rec)
            rec.update({
                'replenishment_base_cost_on_currency':
                replenishment_base_cost_on_currency,
                'replenishment_cost': replenishment_cost
            })

    @api.constrains('replenishment_cost_rule_id')
    def update_replenishment_cost_last_update_by_rule(self):
        self.update_replenishment_cost_last_update()
