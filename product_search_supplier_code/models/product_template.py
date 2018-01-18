# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    sellers_product_code = fields.Char(
        related='seller_ids.product_code',
        string="Vendor Product Code",
    )
