##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .product_search_mixin import MAX_FIELDS, PARAM_ENABLED, PARAM_FIELDS, parse_paths


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_extend_search_fields = fields.Boolean(
        string="Search products by more fields",
        config_parameter=PARAM_ENABLED,
    )
    # same format as the eCommerce parameter: a list of paths from product.template
    product_search_fields = fields.Char(default="[]", config_parameter=PARAM_FIELDS)
    # the field selector widget reads the model to browse from another field
    product_search_model = fields.Char(default="product.template", readonly=True)
    product_search_field_1 = fields.Char(
        string="Field 1",
        compute="_compute_product_search_field",
        inverse="_inverse_product_search_field",
        readonly=False,
    )
    product_search_field_2 = fields.Char(
        string="Field 2",
        compute="_compute_product_search_field",
        inverse="_inverse_product_search_field",
        readonly=False,
    )
    product_search_field_3 = fields.Char(
        string="Field 3",
        compute="_compute_product_search_field",
        inverse="_inverse_product_search_field",
        readonly=False,
    )

    def _search_fields_list(self):
        self.ensure_one()
        return parse_paths(self.product_search_fields)

    @api.depends("product_search_fields")
    def _compute_product_search_field(self):
        for rec in self:
            paths = rec._search_fields_list()
            for index in range(MAX_FIELDS):
                rec["product_search_field_%s" % (index + 1)] = paths[index] if index < len(paths) else False

    def _inverse_product_search_field(self):
        for rec in self:
            boxes = [rec["product_search_field_%s" % (index + 1)] for index in range(MAX_FIELDS)]
            paths = [path.strip() for path in boxes if path and path.strip()]
            previous = rec._search_fields_list()
            # a parameter nobody edited here is left alone, so saving any other setting never fails
            if paths == previous[:MAX_FIELDS]:
                continue
            # only what changed, and only when it is going to be searched
            if rec.product_extend_search_fields:
                for path in set(paths) - set(previous):
                    rec._check_search_path(path)
            rec.product_search_fields = repr(paths)

    def _check_search_path(self, path):
        """Reject what this user could not search, with the same criterion as the search."""
        error = self.env["product.template"]._search_path_error(path)
        if error:
            raise ValidationError(error)
