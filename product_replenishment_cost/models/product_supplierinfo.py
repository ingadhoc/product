##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
        auto_join=True,
        index=True,
        string='Replenishment Cost Rule',
        track_visibility='onchange',
    )
    net_price = fields.Float(
        inverse='_inverse_net_price',
        compute='_compute_net_price',
        # TODO, activamos store como estaba??
        store=False,
        digits=dp.get_precision('Product Price'),
        help="Net Price",
    )

    @api.multi
    def _inverse_net_price(self):
        """ For now we only implement when product_tmpl_id is set
        """
        for rec in self.filtered('product_tmpl_id'):
            price = rec.net_price
            replenishment_cost_rule_id = rec.replenishment_cost_rule_id
            if replenishment_cost_rule_id:
                rec.price = replenishment_cost_rule_id.compute_rule_inverse(
                    price)
            else:
                rec.price = price

    @api.depends(
        'product_id',
        'price',
        # because of being stored
        'currency_id',
        # and this if we change de date (name field)
        # rule items
        'replenishment_cost_rule_id',
    )
    def _compute_net_price(self):
        """ For now we only implement when product_tmpl_id is set
        """
        for rec in self.filtered('product_tmpl_id'):
            net_price = rec.price
            replenishment_cost_rule_id = rec.replenishment_cost_rule_id
            if replenishment_cost_rule_id:
                net_price = replenishment_cost_rule_id.compute_rule(
                    net_price, rec.product_tmpl_id)
            rec.net_price = net_price
