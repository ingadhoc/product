# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, _, api
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class ProductSaleUom(models.Model):

    _name = 'product.sale.uom'
    _description = 'Product Sale Uom'
    _order = 'sequence'

    sequence = fields.Integer(
        'Sequence',
        default=10,
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template'
    )
    uom_id = fields.Many2one(
        'product.uom',
        string='UOM',
        required=True,
    )

    _sql_constraints = [
        ('uom_uniq', 'unique(product_tmpl_id, uom_id)',
            'UOM mast be unique per Product Template!'),
    ]


class product_template(models.Model):

    """"""

    _inherit = 'product.template'

    uom_category_id = fields.Many2one(
        related='uom_id.category_id'
    )
    sale_uom_ids = fields.One2many(
        'product.sale.uom',
        'product_tmpl_id',
        copy=True,
        string='Sale UOMs',
        help="Only uoms in this list will be available in sale order lines. "
        "If none is specified, then all uoms of product uom category will be "
        "available."
    )

    @api.one
    @api.constrains('sale_uom_ids', 'uom_id')
    def _check_uoms(self):
        sale_uom_categories = self.sale_uom_ids.mapped('uom_id.category_id')
        if (
                len(sale_uom_categories) > 1 or
                (sale_uom_categories and
                    sale_uom_categories != self.uom_id.category_id)
        ):
            raise Warning(_('Sale UOMs Category must be of the same \
                UOM Category as Product Unit of Measure'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
