# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # TODO this field should be move to PRC (product_replenishment_cost)
    replenishment_cost_last_update = fields.Datetime(
        'Replenishment Cost Last Update',
        track_visibility='onchange',
    )
    # TODO this field should be move to PRC (product_replenishment_cost)
    replenishment_base_cost = fields.Float(
        'Replenishment Base Cost',
        digits=dp.get_precision('Product Price'),
        track_visibility='onchange',
        help="Replanishment Cost expressed in 'Replenishment Base Cost "
        "Currency'."
    )
    replenishment_base_cost_currency_id = fields.Many2one(
        'res.currency',
        'Replenishment Base Cost Currency',
        track_visibility='onchange',
        help="Currency used for the Replanishment Base Cost."
    )
    # for now we make replenshiment cost field only on template and not in
    # product (this should be done in PRC)
    replenishment_cost = fields.Float(
        compute='_get_replenishment_cost',
        string='Replenishment Cost',
        store=False,
        digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases."
    )

    @api.model
    def cron_update_cost_from_replenishment_cost(self):
        # como es property no podemos hacer el search
        return self.search([])._update_cost_from_replenishment_cost()

    @api.multi
    def _update_cost_from_replenishment_cost(self):
        for rec in self:
            if rec.cost_method != 'standard' or not rec.replenishment_cost:
                continue
            rec.standard_price = rec.replenishment_cost
        return True

    @api.one
    @api.constrains(
        'replenishment_base_cost',
        'replenishment_base_cost_currency_id',
    )
    def update_replenishment_cost_last_update(self):
        self.replenishment_cost_last_update = fields.Datetime.now()

    @api.one
    @api.depends(
        'currency_id',
        'replenishment_base_cost',
        # because of being stored
        'replenishment_base_cost_currency_id.rate_ids.rate',
        # and this if we change de date (name field)
        'replenishment_base_cost_currency_id.rate_ids.name',
    )
    def _get_replenishment_cost(self):
        self.replenishment_cost = self.get_replenishment_cost_currency()

    @api.multi
    def get_replenishment_cost_currency(self):
        self.ensure_one()
        from_currency = self.replenishment_base_cost_currency_id
        to_currency = self.currency_id
        replenishment_cost = False
        if from_currency and to_currency:
            replenishment_cost = self.replenishment_base_cost
            if from_currency != to_currency:
                replenishment_cost = from_currency.compute(
                    replenishment_cost, to_currency, round=False)
        return replenishment_cost


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # we make it related to prod template because for now we want it only
    # on prod template
    replenishment_cost = fields.Float(
        related='product_tmpl_id.replenishment_cost',
        store=False,
    )
