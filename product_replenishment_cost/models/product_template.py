##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier_currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_supplier_data',
    )
    supplier_price = fields.Float(
        string='Supplier Price',
        compute='_compute_supplier_data',
        digits='Product Price',
    )
    standard_price = fields.Float(
        string='Accounting Cost',
    )
    replenishment_cost = fields.Float(
        compute='_compute_replenishment_cost',
        # TODO, activamos store como estaba??
        store=False,
        digits='Product Price',
        help="Replenishment cost on the currency of the product",
    )
    replenishment_cost_last_update = fields.Datetime(
        tracking=True,
        compute='_compute_replenishment_cost_last_update',
        store=True,
        help="Date of the last update of replenishment base cost or its currency"
    )
    replenishment_base_cost = fields.Float(
        digits='Product Price',
        tracking=True,
        help="Replanishment Cost expressed in 'Replenishment Base Cost "
        "Currency'."
    )
    replenishment_base_cost_currency_id = fields.Many2one(
        'res.currency',
        'Replenishment Base Cost Currency',
        auto_join=True,
        tracking=True,
        help="Currency used for the Replanishment Base Cost.",
        default=lambda self: self.env.company.currency_id.id
    )
    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
        auto_join=True,
        index=True,
        tracking=True,
    )
    replenishment_base_cost_on_currency = fields.Float(
        compute='_compute_replenishment_cost',
        help='Replenishment cost on replenishment base cost currency',
        digits='Product Price',
    )
    replenishment_cost_type = fields.Selection(
        [('supplier_price', 'Main Supplier Price'),
         ('last_supplier_price', 'Last Supplier Price'),
         ('manual', 'Manual')],
        default='manual',
        required=True,
    )

    @api.depends_context('company')
    @api.depends('seller_ids.net_price', 'seller_ids.currency_id', 'seller_ids.company_id', 'replenishment_cost_type')
    def _compute_supplier_data(self):
        """ Lo ideal seria utilizar campo related para que segun los permisos
         del usuario tome el seller_id que corresponda, pero el tema es que el
         cron se corre con admin y entonces siempre va a tomar el primer seller
        sin importar si estamos usando un force_company para poder definir rel
         costo en distintas compañias.
        Basicamente usamos regla analoga a la que viene por defecto para los
         sellers donde se puede ver si
        no tiene cia o es cia del usuario.
        """
        company_id = self.env.company.id
        for rec in self:
            seller_ids = rec.seller_ids.filtered(lambda x: not x.company_id or x.company_id.id == company_id)
            if rec.replenishment_cost_type == 'last_supplier_price':
                seller_ids = seller_ids.sorted(key='last_date_price_updated', reverse=True)
            rec.update({
                'supplier_price': seller_ids and seller_ids[0].net_price or 0.0,
                'supplier_currency_id': seller_ids and seller_ids[0].currency_id or self.env['res.currency'],
            })

    @api.model
    def cron_update_cost_from_replenishment_cost(self, limit=None, company_ids=None):

        # allow force_company for backward compatibility
        force_company = self._context.get('force_company', False)
        if force_company and company_ids:
            raise ValidationError(_(
                "The argument 'company_ids' and the key 'force_company' on the context can't be used together"))

        # use company_ids or force_company or search for all companies
        if force_company:
            company_ids = [force_company]
        elif not company_ids:
            company_ids = self.env['res.company'].search([]).ids

        for company_id in company_ids:
            _logger.info('Running cron update cost from replenishment for company %s', company_id)
            self.with_company(company=company_id).with_context(prefetch_fields=False, bypass_base_automation=True).search(
                [], limit=limit)._update_cost_from_replenishment_cost()

    def _update_cost_from_replenishment_cost(self):
        """
        If we came from tree list, we update only in selected list
        Actulizamos product.product ya que el standard_price esta en ese modelo
        """
        prec = self.env['decimal.precision'].precision_get('Product Price')

        # clave hacerlo en product.product por velocidad (relativo a
        # campos standard_price)
        company = self.env.company
        products = self.with_context(tracking_disable=True).env['product.product'].search(
            [('product_tmpl_id.id', 'in', self.ids)])
        for product in products.filtered('replenishment_cost'):
            replenishment_cost = product.replenishment_cost
            if product.currency_id != product.cost_currency_id:
                replenishment_cost = product.currency_id._convert(
                    replenishment_cost, product.cost_currency_id,
                    product.company_id or company, fields.Date.today(),
                    round=True)
            if float_compare(product.standard_price, replenishment_cost, precision_digits=prec) != 0:
                    product.standard_price = replenishment_cost
        return True

    @api.depends(
        'replenishment_cost_type',
        'replenishment_base_cost',
        'replenishment_base_cost_currency_id',
        'supplier_price',
        'supplier_currency_id',
        'replenishment_cost_rule_id.item_ids.sequence',
        'replenishment_cost_rule_id.item_ids.percentage_amount',
        'replenishment_cost_rule_id.item_ids.fixed_amount',
    )
    def _compute_replenishment_cost_last_update(self):
        self.replenishment_cost_last_update = fields.Datetime.now()

    # TODO ver si necesitamos borrar estos depends o no, por ahora
    # no parecen afectar performance y sirvern para que la interfaz haga
    # el onchange, pero no son fundamentales porque el campo no lo storeamos
    @api.depends(
        'currency_id',
        'supplier_price',
        'supplier_currency_id',
        'replenishment_cost_type',
        'replenishment_base_cost',
        # beccause field is not stored anymore we only keep currency and
        # rule
        # 'replenishment_base_cost_currency_id',
        # # because of being stored
        'replenishment_base_cost_currency_id.rate_ids.rate',
        # # and this if we change de date (name field)
        # 'replenishment_base_cost_currency_id.rate_ids.name',
        # rule items
        'replenishment_cost_rule_id.item_ids.sequence',
        'replenishment_cost_rule_id.item_ids.percentage_amount',
        'replenishment_cost_rule_id.item_ids.fixed_amount',
    )
    @api.depends_context('force_company')
    def _compute_replenishment_cost(self):
        _logger.info('Getting replenishment cost for %s products' % len(self.ids))
        company = self.env.company
        date = fields.Date.today()
        for rec in self:
            product_currency = rec.currency_id
            rec.replenishment_base_cost_on_currency = 0.0
            rec.replenishment_cost = 0.0
            if rec.replenishment_cost_type in ['supplier_price', 'last_supplier_price']:
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
