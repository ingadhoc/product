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

    def _default_replenishment_base_cost_currency_id(self):
        return self.env.user.company_id.currency_id.id

    replenishment_cost = fields.Float(
        compute='_compute_replenishment_cost',
        # TODO, activamos store como estaba??
        store=False,
        digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")

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
        default=_default_replenishment_base_cost_currency_id
    )

    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
        auto_join=True,
        index=True,
        string='Replenishment Cost Rule',
        track_visibility='onchange',
    )

    replenishment_base_cost_on_currency = fields.Float(
        compute='_compute_replenishment_cost',
        digits=dp.get_precision('Product Price'),
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
        """
        # hacemos search de nuevo por si se llama desde vista lista
        commit_transaction = self.env.context.get('commit_transaction')
        domain = [
            ('replenishment_base_cost', '!=', False),
            ('replenishment_base_cost_currency_id', '!=', False),
        ]
        if self:
            domain.append(('id', 'in', self.ids))

        batch_size = 1000
        product_ids = self.search(domain).ids
        sliced_product_ids = [
            product_ids[i:i + batch_size] for i in range(
                0, len(product_ids), batch_size)]
        cr = self.env.cr
        run = 0
        prec = self.env['decimal.precision'].precision_get('Product Price')
        for product_ids in sliced_product_ids:
            run += 1
            # hacemos invalidate cache para que no haga prefetch de todos,
            # solo los del slice
            self.invalidate_cache()
            recs = self.browse(product_ids)
            _logger.info(
                'Running update update cost for %s products. Run %s of %s' % (
                    len(recs), run, len(sliced_product_ids)))
            for rec in recs:
                replenishment_cost = rec.replenishment_cost
                # TODO we should check if standar_price type is standar and
                # not by quants or similar, we remove that because it makes
                # it slower
                if not replenishment_cost:
                    continue
                # to avoid writing if there are no changes, also to avoid
                # creating records on product_price_history table
                if float_compare(
                        rec.standard_price, replenishment_cost,
                        precision_digits=prec) == 0:
                    continue
                # standard_price is stored on variants (product.product), we
                # force the update of all the variants
                rec.product_variant_ids.write(
                    {'standard_price': replenishment_cost})
                # we can not use sql because standar_price is a property,
                # perhups we can do it writing directly on the property but
                # we need to check if record exists, we can copy some code of
                # def set_multi
                # tal vez mejor que meter mano en esto hacer que solo se
                # actualicen los que se tienen que actualizar
                # seguramente en la v10 se mejoro el metodo de set de property
                # tmb
                # cr.execute(
                #     "UPDATE product_template SET standard_price=%s WHERE "
                #     "id=%s", (replenishment_cost, rec.id))

            # commit update (fo free memory?) also to have results stored
            # in the future, if we store the date, we can update only newones

            # principalmente agregamos esto por error en migracion pero tmb
            # para que solo se haga el commit por cron
            if commit_transaction:
                cr.commit()  # pylint: disable=invalid-commit
            _logger.info('Finish updating cost of run %s', run)

        return True

    @api.constrains(
        'replenishment_base_cost',
        'replenishment_base_cost_currency_id',
    )
    def update_replenishment_cost_last_update(self):
        self.write({'replenishment_cost_last_update': fields.Datetime.now()})

    # TODO ver si necesitamos borrar estos depends o no, por ahora
    # no parecen afectar performance y sirvern para que la interfaz haga
    # el onchange, pero no son fundamentales porque el campo no lo storeamos
    @api.depends(
        'currency_id',
        'replenishment_base_cost',
        # because of being stored
        'replenishment_base_cost_currency_id.rate_ids.rate',
        # and this if we change de date (name field)
        'replenishment_base_cost_currency_id.rate_ids.name',
        # rule items
        'replenishment_cost_rule_id.item_ids.sequence',
        'replenishment_cost_rule_id.item_ids.percentage_amount',
        'replenishment_cost_rule_id.item_ids.fixed_amount',
    )
    def _compute_replenishment_cost(self):
        _logger.info(
            'Getting replenishment cost currency for ids %s' % self.ids)
        for rec in self:
            replenishment_cost = rec.get_replenishment_cost_currency(
                rec.replenishment_base_cost_currency_id,
                rec.currency_id,
                rec.replenishment_base_cost,
            )
            replenishment_base_cost_on_currency = replenishment_cost
            if rec.replenishment_cost_rule_id:
                replenishment_cost =\
                    rec.replenishment_cost_rule_id.compute_rule(
                        replenishment_base_cost_on_currency, rec)
            rec.update({
                'replenishment_base_cost_on_currency':
                replenishment_base_cost_on_currency,
                'replenishment_cost': replenishment_cost
            })

    @api.model
    def get_replenishment_cost_currency(
            self, from_currency, to_currency, base_cost):
        replenishment_cost = False
        if from_currency and to_currency:
            replenishment_cost = base_cost
            if from_currency != to_currency:
                replenishment_cost = from_currency.compute(
                    replenishment_cost, to_currency, round=False)
        return replenishment_cost

    @api.constrains('replenishment_cost_rule_id')
    def update_replenishment_cost_last_update_by_rule(self):
        self.update_replenishment_cost_last_update()
