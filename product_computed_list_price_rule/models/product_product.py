# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
# import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    computed_list_price_rule_id = fields.Many2one(
        'product.computed_list_price.rule',
        string='Sale Price Rule',
        )

    @api.multi
    def get_computed_list_price(self):
        self.ensure_one()
        price = super(ProductTemplate, self).get_computed_list_price()
        if self.computed_list_price_rule_id and price:
            for line in self.computed_list_price_rule_id.item_ids:
                price = price * \
                    (1 + line.percentage_amount / 100.0) + line.fixed_amount
            return price

    # @api.multi
    # def get_computed_list_price_with_rule(self):
    #     # cost = super(ProductTemplate, self).get_replenishment_cost()
    #     cost = self.get_replenishment_cost_currency()
    #     if self.replenishment_cost_rule_id:
    #         for line in self.replenishment_cost_rule_id.item_ids:
    #             cost = cost * \
    #                 (1 + line.percentage_amount / 100.0) + line.fixed_amount
    #     return cost

    # This fields is used for view imp.
    # replenishment_cost_currency_id_copy = fields.Many2one(
    #     related="replenishment_cost_currency_id"
    #     )
    # replenishment_base_cost_on_currency = fields.Float(
    #     compute='_get_replenishment_base_cost_on_currency',
    #     digits=dp.get_precision('Product Price'),
    #     )

    # @api.one
    # @api.depends(
    #     'replenishment_base_cost',
    #     # because of being stored
    #     'replenishment_base_cost_currency_id.rate_ids.rate',
    #     # and this if we change de date (name field)
    #     'replenishment_base_cost_currency_id.rate_ids.name',
    #     )
    # def _get_replenishment_base_cost_on_currency(self):
    #     self.replenishment_base_cost_on_currency = (
    #         self.get_replenishment_cost_currency())

    # @api.one
    # @api.depends(
    #     'replenishment_base_cost',
    #     # because of being stored
    #     'replenishment_base_cost_currency_id.rate_ids.rate',
    #     # and this if we change de date (name field)
    #     'replenishment_base_cost_currency_id.rate_ids.name',
    #     # rule items
    #     'replenishment_cost_rule_id.item_ids.sequence',
    #     'replenishment_cost_rule_id.item_ids.percentage_amount',
    #     'replenishment_cost_rule_id.item_ids.fixed_amount',
    #     )
    # def _get_replenishment_cost(self):
    #     self.replenishment_cost = self.get_replenishment_cost_with_rule()
