##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import api, models

from .ir_access import restrict_product_access


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _access_domain(self, operation):
        return restrict_product_access(self, operation, super()._access_domain(operation))
