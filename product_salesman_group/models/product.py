# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    salesman_group_ids = fields.Many2many(
        'sale.salesman.group', 'prod_template_salesgroup_rel',
        'template_id', 'section_id', string='Salesman Group', )
