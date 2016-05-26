# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import openerp.addons.decimal_precision as dp


class product_template(models.Model):
    _inherit = "product.template"

    published_sale_price = fields.Float(
        'Published Sale Price',
        digits_compute=dp.get_precision('Product Price')
    )
