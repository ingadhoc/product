##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    last_date_price_updated = fields.Datetime(string="Last date price updated",
                                              default=lambda self: fields.Datetime.now())

    replenishment_cost_rule_id = fields.Many2one(
        'product.replenishment_cost.rule',
        auto_join=True,
        index=True,
        string='Replenishment Cost Rule',
    )
    net_price = fields.Float(
        inverse='_inverse_net_price',
        compute='_compute_net_price',
        store=False,
        digits='Product Price',
        help="Net Price",
    )

    def write(self, vals):
        if vals.get('price') and not vals.get('last_date_price_updated'):
            vals.update(last_date_price_updated=fields.Datetime.now())
        return super(ProductSupplierinfo, self).write(vals)

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
        'currency_id',
        # and this if we change de date (name field)
        # rule items
        'replenishment_cost_rule_id.item_ids.sequence',
        'replenishment_cost_rule_id.item_ids.percentage_amount',
        'replenishment_cost_rule_id.item_ids.fixed_amount',
    )
    def _compute_net_price(self):
        """ For now we only implement when product_tmpl_id is set
        """
        product_tmpls = self.filtered('product_tmpl_id')
        (self - product_tmpls).update({'net_price': 0.0})
        for rec in product_tmpls:
            net_price = rec.price
            replenishment_cost_rule_id = rec.replenishment_cost_rule_id
            if replenishment_cost_rule_id:
                net_price = replenishment_cost_rule_id.compute_rule(
                    net_price, rec.product_tmpl_id)
            rec.net_price = net_price
