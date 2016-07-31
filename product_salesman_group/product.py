# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class product_template(models.Model):

    _inherit = 'product.template'

    salesman_group_ids = fields.Many2many(
        'sale.salesman.group', 'prod_template_salesgroup_rel',
        'template_id', 'section_id', string='Salesman Group', )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
