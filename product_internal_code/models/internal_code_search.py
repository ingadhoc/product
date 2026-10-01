##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.fields import Domain


def prepend_internal_code_match(model, results, name, domain, operator, limit):
    """Put the record whose internal code is exactly the term first: the native search
    can fill the limit on its own and leave it out."""
    if not name or not isinstance(name, str):
        return results
    if operator in Domain.NEGATIVE_OPERATORS or not operator.endswith("like"):
        return results
    record = model.search(Domain(domain or Domain.TRUE) & Domain("internal_code", "=", name), limit=1)
    if not record:
        return results
    results = [(record.id, record.display_name)] + [res for res in results if res[0] != record.id]
    return results[:limit] if limit else results
