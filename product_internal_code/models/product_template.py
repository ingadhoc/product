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
        if not any(vals.get("internal_code") for vals in vals_list):
            return super().create(vals_list)
        vals_list = [dict(vals) for vals in vals_list]
        codes = [vals.pop("internal_code", False) for vals in vals_list]
        # Variants exist only after the template create, so they get their code afterwards
        templates = super(ProductTemplate, self.with_context(skip_internal_code_sequence=True)).create(vals_list)
        templates = templates.with_env(self.env)
        for template, code in zip(templates, codes):
            if code:
                template.product_variant_ids[:1].internal_code = code
        templates.product_variant_ids.filtered(lambda product: not product.internal_code)._assign_internal_code()
        return templates

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        results = super().name_search(name, domain, operator, limit)
        return prepend_internal_code_match(self, results, name, domain, operator, limit)
