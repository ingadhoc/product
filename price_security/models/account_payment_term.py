##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sequence = fields.Integer(default=lambda self: self._get_default_sequence())
    payment_term_allowed_ids = fields.Many2many(
        comodel_name="account.payment.term",
        relation="account_payment_term_allowed_rel",
        column1="user_id",
        column2="payment_term_id",
        string="Allowed Payment Terms",
        help="Payment terms that a user with restrictions can select",
    )

    def _get_default_sequence(self):
        last_sequence = self.env["account.payment.term"].search([], order="sequence DESC", limit=1).sequence
        return last_sequence + 1 if last_sequence is not None else 1
