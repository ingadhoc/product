##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    uom_unit_ids = fields.Many2many(
        'uom.uom',
        compute='_compute_uom_unit')

    @api.depends('product_id')
    def _compute_uom_unit(self):
        for rec in self:
            if rec.product_id:
                rec.uom_unit_ids = rec.product_id.get_product_uoms(
                    rec.product_id.uom_id, use='sale')
            else:
                rec.uom_unit_ids = False

    @api.depends('product_id')
    def _compute_product_uom(self):
        super()._compute_product_uom()
        for line in self:
            if line.product_id:
                sale_product_uoms = line.product_id.get_product_uoms(
                    line.product_id.uom_id, use='sale')
                if sale_product_uoms:
                    line.product_uom = sale_product_uoms[0].id

    @api.constrains('product_uom')
    def check_uoms(self):
        if self._context.get('website_id'):
            return True
        for rec in self.filtered('product_id'):
            product = rec.product_id
            sale_product_uoms = product.get_product_uoms(
                product.uom_id, use='sale')
            if rec.product_uom not in sale_product_uoms:
                raise ValidationError(_(
                    "%s unit of measure is not valid for sale,"
                    " please change %s product line with the proper"
                    " uom in order to continue" % (
                        rec.product_uom.name, product.display_name,
                    )))
