##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from ast import literal_eval

from odoo import api, models
from odoo.osv import expression
from odoo.tools.misc import str2bool

LIKE_OPERATORS = ("ilike", "like")
# below three characters a trigram index cannot serve the query
MIN_CHARS = 3
MAX_FIELDS = 3
# a relation as the last step searches by the display name of its records
SEARCHABLE_TYPES = ("char", "text")
PARAM_ENABLED = "product_ux.extend_search_fields"
PARAM_FIELDS = "product_ux.search_fields"


def parse_paths(value):
    """The parameter as a list of paths. Content nobody can read is no configuration."""
    try:
        paths = literal_eval(value or "[]")
    except (ValueError, SyntaxError):
        return []
    if not isinstance(paths, list):
        return []
    return [path.strip() for path in paths if isinstance(path, str) and path.strip()]


def configured_paths(env):
    """Paths from product.template the consultant configured, or nothing."""
    params = env["ir.config_parameter"].sudo()
    if not str2bool(params.get_param(PARAM_ENABLED), default=False):
        return ()
    # the boxes cap it, so a hand edited parameter cannot widen the search either
    return tuple(parse_paths(params.get_param(PARAM_FIELDS))[:MAX_FIELDS])


class ProductSearchMixin(models.AbstractModel):
    _name = "product.search.mixin"
    _description = "Extended Product Search"

    # always searched, so a word of the term can match the product itself
    _search_native_paths = ("name", "default_code")

    @api.model
    def _search_path(self, path):
        """The configured path, from product.template, as this model searches it."""
        return path

    @api.model
    def _extended_search_paths(self):
        paths = tuple(
            path for path in map(self._search_path, configured_paths(self.env)) if not self._search_path_error(path)
        )
        if not paths:
            return ()
        return self._search_native_paths + paths

    @api.model
    def _search_path_error(self, path):
        """Why this user cannot search the path on this model, or None.

        Settings rejects with it and the search skips with it, so both follow the same criterion.
        """
        model = self
        names = path.split(".")
        for index, name in enumerate(names):
            field = model._fields.get(name)
            if field is None:
                return self.env._('Field "%(path)s" does not exist on %(model)s.', path=path, model=model._name)
            if not field._description_searchable:
                return self.env._(
                    '"%s" cannot be searched: it is neither stored nor has a search method.', field.string
                )
            if not field.is_accessible(self.env):
                return self.env._('"%s" is restricted by groups you do not have.', field.string)
            if field.type == "properties":
                # the 18.0 selector offers them, but a property cannot be confirmed to exist
                return self.env._('"%s" holds properties, they cannot be searched.', field.string)
            if field.comodel_name and not self.env[field.comodel_name].has_access("read"):
                return self.env._('You cannot read "%s".', self.env[field.comodel_name]._description)
            if index == len(names) - 1:
                return self._search_last_step_error(field)
            if not field.comodel_name:
                return self.env._('"%s" is not a relational field, the path cannot be followed.', name)
            model = self.env[field.comodel_name]
        return None

    @api.model
    def _search_last_step_error(self, field):
        if field.type == "html":
            return self.env._(
                '"%s" is an HTML field. Searching inside HTML is the main cause of slow searches: use a text field.',
                field.string,
            )
        if field.type in ("binary", "image"):
            return self.env._('"%s" is an attachment, it cannot be searched.', field.string)
        if field.type not in SEARCHABLE_TYPES and not field.comodel_name:
            return self.env._(
                '"%(name)s" is a %(type)s field. Only text fields and relations can be searched.',
                name=field.string,
                type=field.type,
            )
        return None

    @api.model
    def _search_resolved_exactly(self, results, term):
        """Whether the native search picked one product on purpose, by an exact code."""
        return False

    @api.model
    def _extended_search_domain(self, term, operator="ilike"):
        """Every word, in any order and on any of the paths, in a single domain."""
        if not isinstance(term, str):
            return None
        # a short word would be a full scan on every path
        words = [word for word in term.split() if len(word) >= MIN_CHARS]
        paths = words and self._extended_search_paths()
        if not paths:
            return None
        return expression.AND([expression.OR([[(path, operator, word)] for path in paths]) for word in words])

    @api.model
    def _extend_name_search(self, results, term, args, operator, limit):
        """Complete the native result, only if it did not fill the limit."""
        if operator not in LIKE_OPERATORS or (limit and len(results) >= limit):
            return results
        extra = self._extended_search_domain(term, operator)
        if extra is None or self._search_resolved_exactly(results, term):
            return results
        ids = [res[0] for res in results]
        full_domain = expression.AND([args or [], extra, [("id", "not in", ids)]])
        records = self.browse(self._search(full_domain, limit=limit and limit - len(ids)))
        # same as the native name_search, so the added rows read like the others
        return results + [(record.id, record.display_name) for record in records.sudo()]
