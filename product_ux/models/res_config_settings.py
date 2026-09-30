##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .product_search_mixin import MAX_FIELDS, PARAM_ENABLED, PARAM_FIELDS, parse_paths

# a relation as the last step searches by the display name of its records
SEARCHABLE_TYPES = ("char", "text")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_extend_search_fields = fields.Boolean(
        string="Search products by more fields",
        config_parameter=PARAM_ENABLED,
    )
    # same format as the eCommerce parameter: a list of paths from product.template
    product_search_fields = fields.Char(default="[]", config_parameter=PARAM_FIELDS)
    # the field_selector widget reads the model to browse from another field
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
            # a parameter nobody edited here is left alone, so saving any other setting never fails
            if paths == rec._search_fields_list()[:MAX_FIELDS]:
                continue
            for path in paths:
                rec._check_search_path(path)
            rec.product_search_fields = repr(paths)

    def _check_search_path(self, path):
        """Reject what Odoo cannot search, or what would degrade the search."""
        model = self.env["product.template"]
        parts = path.split(".")
        for index, name in enumerate(parts):
            field = model._fields.get(name)
            if field is None:
                raise ValidationError(
                    self.env._(
                        'Field "%(path)s" does not exist on %(model)s.',
                        path=path,
                        model=model._name,
                    )
                )
            self._check_searchable(field)
            if index == len(parts) - 1:
                self._check_last_step(field)
            elif not field.comodel_name:
                raise ValidationError(self.env._('"%s" is not a relational field, the path cannot be followed.', name))
            else:
                model = self.env[field.comodel_name]

    def _check_searchable(self, field):
        """Every step has to be searchable on its own, or the domain breaks in SQL."""
        if not field._description_searchable:
            raise ValidationError(
                self.env._(
                    '"%s" cannot be searched: it is neither stored nor has a search method.',
                    field.string,
                )
            )
        if field.groups:
            raise ValidationError(
                self.env._(
                    '"%s" is restricted by groups: users without access would get an error when searching.',
                    field.string,
                )
            )

    def _check_last_step(self, field):
        if field.type == "html":
            raise ValidationError(
                self.env._(
                    '"%s" is an HTML field. Searching inside HTML is the main cause of '
                    "slow searches: use a text field.",
                    field.string,
                )
            )
        if field.type in ("binary", "image"):
            raise ValidationError(self.env._('"%s" is an attachment, it cannot be searched.', field.string))
        if field.type not in SEARCHABLE_TYPES and not field.comodel_name:
            raise ValidationError(
                self.env._(
                    '"%(name)s" is a %(type)s field. Only text fields and relations can be searched.',
                    name=field.string,
                    type=field.type,
                )
            )
