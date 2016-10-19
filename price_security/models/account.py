# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    sequence = fields.Integer(
        string='Sequence')
