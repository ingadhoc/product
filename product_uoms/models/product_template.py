##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    uom_category_id = fields.Many2one(
        related='uom_id.category_id',
    )
    uom_ids = fields.One2many(
        'product.uoms',
        'product_tmpl_id',
        copy=True,
        string='UOMs',
        oldname='sale_uom_ids',
        help="Only uoms in this list will be available. "
        "If none is specified, then all uoms of product uom category will be "
        "available.",
    )

    @api.constrains('uom_ids', 'uom_id')
    def _check_uoms(self):
        for rec in self:
            uom_categories = rec.uom_ids.mapped(
                'uom_id.category_id')
            if (
                    len(uom_categories) > 1 or
                    (uom_categories and
                        uom_categories != rec.uom_id.category_id)
            ):
                raise ValidationError(_(
                    'UOMs Category must be of the same '
                    'UOM Category as Product Unit of Measure'))
