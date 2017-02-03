# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models
# from openerp.osv import expression


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    # we create this field and make it stored so we can group by it
    main_seller_id = fields.Many2one(
        related='seller_ids.name', string="Main Seller", store=True,
    )
