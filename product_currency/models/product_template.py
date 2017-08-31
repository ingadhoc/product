# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
from openerp.osv import fields as old_fields
# from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = "product.template"

    force_currency_id = fields.Many2one(
        'res.currency',
        'Force Currency',
        help='Use this currency instead of the product company currency'
    )

    def _product_currency(self, cr, uid, ids, name, arg, context=None):
        res = super(ProductTemplate, self)._product_currency(
            cr, uid, ids, name, arg, context=context)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.force_currency_id:
                res[rec.id] = rec.force_currency_id.id
        return res

    _columns = {
        'currency_id': old_fields.function(
            _product_currency, type='many2one', relation='res.currency',
            string='Currency'),
    }
