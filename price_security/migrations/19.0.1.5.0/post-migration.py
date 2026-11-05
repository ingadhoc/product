from odoo import Command
from odoo.upgrade import util

TARGETS = [
    ("account.payment.term", "payment_term_allowed_ids"),
    ("product.pricelist", "pricelist_allowed_ids"),
]


def fill_allowed_from_sequence(records, allowed_field):
    """Seed the allowed list of every record from the sequence order.

    Until 18.0 a restricted user could pick any payment term or pricelist whose
    sequence was lower or equal than the one set on the contact. 19.0 replaced
    that rule by an explicit allowed list, so a database coming from an older
    version needs the equivalent list to keep behaving the same way.
    """
    for record in records:
        allowed = records.filtered(lambda rec: rec.sequence <= record.sequence) - record
        record[allowed_field] = [Command.set(allowed.ids)]


def migrate(cr, version):
    env = util.env(cr)
    for model, allowed_field in TARGETS:
        # Archived records count: the pre-19.0 check only looked at the sequence.
        records = env[model].with_context(active_test=False).search([])
        # Anything already set means the allowed lists were configured by hand, so the
        # sequences are no longer the source of truth for this model.
        if records.filtered(allowed_field):
            continue
        fill_allowed_from_sequence(records, allowed_field)
