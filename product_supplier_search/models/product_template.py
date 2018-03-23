# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models
# from odoo.osv import expression


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    # we create this field and make it stored so we can group by it
    main_seller_id = fields.Many2one(
        related='seller_ids.name', string="Main Seller", store=True,
    )
