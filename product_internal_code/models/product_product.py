##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    internal_code = fields.Char(
        copy=False,
        index="btree_not_null",
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
