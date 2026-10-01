##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models

from .internal_code_search import prepend_internal_code_match


class ProductTemplate(models.Model):
    _inherit = "product.template"

    internal_code = fields.Char(related="product_variant_ids.internal_code", string="Internal Code", readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("internal_code"):
                self = self.with_context(default_internal_code=vals.get("internal_code"))
        return super().create(vals_list)

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        results = super().name_search(name, domain, operator, limit)
        return prepend_internal_code_match(self, results, name, domain, operator, limit)
