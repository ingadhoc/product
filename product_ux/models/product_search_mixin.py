##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from ast import literal_eval

from odoo import api, models
from odoo.fields import Domain

LIKE_OPERATORS = ("ilike", "like")
# below three characters a trigram index cannot serve the query
MIN_CHARS = 3
MAX_FIELDS = 3
# always searched, so a word of the term can match the product itself
NATIVE_PATHS = ("name", "default_code")
PARAM_ENABLED = "product_ux.extend_search_fields"
PARAM_FIELDS = "product_ux.search_fields"


def configured_paths(env):
    """Paths from product.template the consultant configured, or nothing."""
    params = env["ir.config_parameter"].sudo()
    if not params.get_param(PARAM_ENABLED):
        return ()
    try:
        paths = literal_eval(params.get_param(PARAM_FIELDS) or "[]")
    except (ValueError, SyntaxError):
        return ()
    return tuple(path for path in paths if isinstance(path, str) and path.strip())


class ProductSearchMixin(models.AbstractModel):
    _name = "product.search.mixin"
    _description = "Extended Product Search"

    # prefix needed to reach a product.template field from this model
    _search_path_prefix = ""

    @api.model
    def _extended_search_paths(self):
        paths = configured_paths(self.env)
        if not paths:
            return ()
        return NATIVE_PATHS + tuple(self._search_path_prefix + path for path in paths)

    @api.model
    def _extended_search_domain(self, term):
        """Every word, in any order and on any of the paths, in a single domain."""
        paths = self._extended_search_paths()
        if not paths or not isinstance(term, str) or len(term.strip()) < MIN_CHARS:
            return None
        return Domain.AND([Domain.OR([Domain(path, "ilike", word) for path in paths]) for word in term.split()])

    @api.model
    def _extend_name_search(self, results, term, domain, operator, limit):
        """Complete the native result, only if it did not fill the limit."""
        if operator not in LIKE_OPERATORS or (limit and len(results) >= limit):
            return results
        extra = self._extended_search_domain(term)
        if extra is None:
            return results
        ids = [res[0] for res in results]
        full_domain = Domain.AND([Domain(domain or Domain.TRUE), extra, Domain("id", "not in", ids)])
        records = self.browse(self._search(full_domain, limit=limit and limit - len(ids)))
        return results + [(record.id, record.display_name) for record in records]
