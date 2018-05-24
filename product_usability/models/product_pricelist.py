# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    # overwrite the methot do avoid error on all(ids) section
    def name_get(self, cr, uid, ids, context=None):
        result = []
        # if not all(ids):
        #     return result
        for pl in self.browse(cr, uid, ids, context=context):
            name = pl.name + ' (' + pl.currency_id.name + ')'
            result.append((pl.id, name))
        return result
