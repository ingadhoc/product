##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models

from .internal_code_search import prepend_internal_code_match


class ProductProduct(models.Model):
    _inherit = "product.product"

    internal_code = fields.Char(
        copy=False,
        index="btree_not_null",
        help="Unique internal code of the product; if left empty it is generated " "automatically from a sequence.",
    )

    _internal_code_uniq = models.Constraint(
        "unique (internal_code)",
        "Internal Code must be unique!",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("internal_code", False) and not self.env.context.get("default_internal_code", False):
                vals["internal_code"] = self.env["ir.sequence"].next_by_code("product.internal.code")
        return super().create(vals_list)

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        results = super().name_search(name, domain, operator, limit)
        return prepend_internal_code_match(self, results, name, domain, operator, limit)
