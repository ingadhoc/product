##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sequence = fields.Integer(default=lambda self: self._get_default_sequence())

    def _get_default_sequence(self):
        last_sequence = self.env["account.payment.term"].search([], order="sequence DESC", limit=1).sequence
        return last_sequence + 1 if last_sequence is not None else 1
