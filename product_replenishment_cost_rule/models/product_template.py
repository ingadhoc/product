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
        compute='_get_replenishment_base_cost_on_currency',
        string='Replenishment Base Cost on Currency',
        digits=dp.get_precision('Product Price'),
    )

    @api.one
    @api.constrains('replenishment_cost_rule_id')
    def update_replenishment_cost_last_update_by_rule(self):
        self.update_replenishment_cost_last_update()

    @api.multi
    @api.depends(
        'currency_id',
        'replenishment_base_cost',
        'replenishment_base_cost_currency_id.rate_ids.rate',
        'replenishment_base_cost_currency_id.rate_ids.name',
    )
    def _get_replenishment_base_cost_on_currency(self):
        super(ProductTemplate, self)._get_replenishment_cost()
        for rec in self:
            rec.replenishment_base_cost_on_currency = rec.replenishment_cost

    @api.multi
    # TODO ver si necesitamos borrar estos depends o no, por ahora
    # no parecen afectar performance y sirvern para que la interfaz haga
    # el onchange, pero no son fundamentales porque el campo no lo storeamos
    @api.depends(
        'replenishment_base_cost_on_currency',
        # rule items
        'replenishment_cost_rule_id.item_ids.sequence',
        'replenishment_cost_rule_id.item_ids.percentage_amount',
        'replenishment_cost_rule_id.item_ids.fixed_amount',
    )
    def _get_replenishment_cost(self):
        for rec in self:
            cost = rec.replenishment_base_cost_on_currency
            if rec.replenishment_cost_rule_id:
                rec.replenishment_cost = \
                    rec.replenishment_cost_rule_id.compute_rule(cost, rec)
