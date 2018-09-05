##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    uom_unit_ids = fields.Many2many(
        'product.uom',
        compute='_compute_uom_unit',
    )

    @api.depends('product_id')
    def _compute_uom_unit(self):
        for rec in self.filtered('product_id'):
            rec.uom_unit_ids = rec.product_id.get_product_uoms(
                rec.product_id.uom_id, use='stock')

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        product_uom_id = None
        product_uom_domain = None
        if self.product_id:
            product = self.product_id
            stock_product_uoms = product.get_product_uoms(
                product.uom_id, use='stock')
            if stock_product_uoms:
                product_uom_id = stock_product_uoms[0].id
                # we do this because odoo overwrite view domain
                product_uom_domain = [('id', 'in', stock_product_uoms.ids)]
        res = super(StockMoveLine, self).onchange_product_id()
        if product_uom_id:
            self.product_uom_id = product_uom_id
        if product_uom_domain:
            res = {'domain': {'product_uom_id': product_uom_domain}}
        return res

    @api.constrains('product_uom_id')
    def check_uoms(self):
        for rec in self:
            product = rec.product_id
            stock_product_uoms = product.get_product_uoms(
                product.uom_id, use='stock')
            if rec.product_uom_id not in stock_product_uoms:
                raise ValidationError(_(
                    "%s unit of measure is not valid for operations,"
                    " please change %s product line with the proper"
                    " uom in order to continue" % (
                        rec.product_uom_id.name, product.display_name,
                    )))
