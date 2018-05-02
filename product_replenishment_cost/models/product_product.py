##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # This becase this module need to write the value in all companies
    standard_price = fields.Float(company_dependent=False)
