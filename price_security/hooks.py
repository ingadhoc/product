# Part of Odoo. See LICENSE file for full copyright and licensing details.


def post_init_hook(env):
    terms = env["account.payment.term"].search([], order="id ASC")
    for idx, term in enumerate(terms, start=1):
        term.sequence = idx
