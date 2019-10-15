##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    uom_unit_ids = fields.Many2many(
        'uom.uom',
        compute='_compute_uom_unit')

    @api.depends('product_id')
    def _compute_uom_unit(self):
        for rec in self.filtered('product_id'):
            rec.uom_unit_ids = rec.product_id.get_product_uoms(
                rec.product_id.uom_po_id, use='purchase')

    @api.onchange('product_id')
    def onchange_product_id(self):
        product_uom = None
        product_uom_domain = None
        if self.product_id:
            product = self.product_id
            purchase_product_uoms = product.get_product_uoms(
                product.uom_po_id, use='purchase')
            if purchase_product_uoms:
                product_uom = purchase_product_uoms[0].id
                # we do this because odoo overwrite view domain
                product_uom_domain = [('id', 'in', purchase_product_uoms.ids)]
        res = super().onchange_product_id()
        if product_uom:
            self.product_uom = product_uom
        if product_uom_domain:
            res = {'domain': {'product_uom': product_uom_domain}}
        return res

    @api.constrains('product_uom')
    def check_uoms(self):
        for rec in self:
            product = rec.product_id
            purchase_product_uoms = product.get_product_uoms(
                product.uom_po_id, use='purchase')
            if rec.product_uom not in purchase_product_uoms:
                raise ValidationError(_(
                    "%s unit of measure is not valid for purchase,"
                    " please change %s product line with the proper"
                    " uom in order to continue" % (
                        rec.product_uom.name, product.display_name,
                    )))
