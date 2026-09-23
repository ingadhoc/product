##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from ast import literal_eval

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .product_search_mixin import MAX_FIELDS, PARAM_ENABLED, PARAM_FIELDS

SEARCHABLE_TYPES = ("char", "text")
# a path into the variants makes Postgres re-run the subplan once per candidate
# template: measure it before allowing it (task 59012)
FORBIDDEN_RELATION = "product_variant_ids"


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

    def _search_fields_list(self, strict=False):
        """The parameter as a list of paths. Bad content only raises on save."""
        self.ensure_one()
        try:
            paths = literal_eval(self.product_search_fields or "[]")
        except (ValueError, SyntaxError):
            paths = None
        if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
            if strict:
                raise ValidationError(self.env._("The search fields must be a list of fields."))
            return []
        return [path.strip() for path in paths if path.strip()]

    @api.depends("product_search_fields")
    def _compute_product_search_field(self):
        for rec in self:
            paths = rec._search_fields_list()
            for index in range(MAX_FIELDS):
                rec["product_search_field_%s" % (index + 1)] = paths[index] if index < len(paths) else False

    def _inverse_product_search_field(self):
        for rec in self:
            paths = [rec["product_search_field_%s" % (index + 1)] for index in range(MAX_FIELDS)]
            rec.product_search_fields = repr([path.strip() for path in paths if path and path.strip()])

    @api.constrains("product_search_fields")
    def _check_product_search_fields(self):
        for rec in self:
            paths = rec._search_fields_list(strict=True)
            if len(paths) > MAX_FIELDS:
                raise ValidationError(
                    rec.env._(
                        "Up to %s fields can be searched: more of them make every " "keystroke slower for everybody.",
                        MAX_FIELDS,
                    )
                )
            for path in paths:
                rec._check_search_path(path)

    def _check_search_path(self, path):
        """Reject what cannot be searched in SQL or degrades the search."""
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
            if index < len(parts) - 1:
                if not field.comodel_name:
                    raise ValidationError(
                        self.env._('"%s" is not a relational field, the path cannot be followed.', name)
                    )
                if name == FORBIDDEN_RELATION:
                    raise ValidationError(
                        self.env._(
                            'Searching through "%s" is not allowed yet: that query shape is '
                            "the one that makes the native product search slow, and it has "
                            "to be measured first.",
                            field.string,
                        )
                    )
                model = self.env[field.comodel_name]
            else:
                self._check_searchable(field)

    def _check_searchable(self, field):
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
        if not field.store:
            raise ValidationError(
                self.env._('"%s" is not stored in the database, it cannot be searched in SQL.', field.string)
            )
        if field.type not in SEARCHABLE_TYPES:
            raise ValidationError(
                self.env._(
                    '"%(name)s" is a %(type)s field. Only text fields can be searched.',
                    name=field.string,
                    type=field.type,
                )
            )
        if field.groups:
            raise ValidationError(
                self.env._(
                    '"%s" is restricted by groups: users without access would get an error ' "when searching.",
                    field.string,
                )
            )
