# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
        auto_join=True,
        string='Replenishment Cost Rule',
        track_visibility='onchange',
    )
    replenishment_base_cost_on_currency = fields.Float(
        compute='_get_replenishment_cost',
        string='Replenishment Base Cost on Currency',
        digits=dp.get_precision('Product Price'),
    )

    @api.one
    @api.constrains('replenishment_cost_rule_id')
    def update_replenishment_cost_last_update_by_rule(self):
        self.update_replenishment_cost_last_update()

    @api.multi
    # TODO ver si necesitamos borrar estos depends o no, por ahora
    # no parecen afectar performance y sirvern para que la interfaz haga
    # el onchange, pero no son fundamentales porque el campo no lo storeamos
    @api.depends(
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
    def _get_replenishment_cost(self):
        """
        We overwrite rep cost currency method with this new method, no super
        call
        """
        _logger.info(
            'Getting replenishment cost with rule for %s products' % (
                len(self.ids)))
        # TODO tal vez para mejorar perfomance podriamos agrupar por aquellos
        # que tienen la misma rul y hacerlos juntos. igual no se que tanto
        # ganariamos ya que seguramente el prefetch de las rules ya hace que
        # vengan del cache
        for rec in self:
            cost = rec.get_replenishment_cost_currency(
                rec.replenishment_base_cost_currency_id,
                rec.currency_id,
                rec.replenishment_base_cost,
            )
            rec.replenishment_base_cost_on_currency = cost
            if rec.replenishment_cost_rule_id:
                rec.replenishment_cost = rec.replenishment_cost_rule_id.compute_rule(cost)
