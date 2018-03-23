##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    salesman_group_ids = fields.Many2many(
        'sale.salesman.group', 'prod_template_salesgroup_rel',
        'template_id', 'section_id', string='Salesman Group', )
