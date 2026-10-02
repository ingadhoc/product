##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.fields import Domain


def complete_with_internal_code(model, results, name, domain, operator, limit):
    """Add what the internal code matches exactly, without changing the native result."""
    if not name or not isinstance(name, str) or (limit and len(results) >= limit):
        return results
    if operator in Domain.NEGATIVE_OPERATORS or not operator.endswith("like"):
        return results
    found_ids = [res[0] for res in results]
    extra = Domain(domain or Domain.TRUE) & Domain("internal_code", "=", name) & Domain("id", "not in", found_ids)
    records = model.search(extra, limit=limit and limit - len(found_ids))
    return results + [(record.id, record.display_name) for record in records]
