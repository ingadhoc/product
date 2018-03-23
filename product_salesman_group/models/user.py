##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResUsers(models.Model):

    _inherit = "res.users"

    salesman_group_id = fields.Many2one(
        'sale.salesman.group',
        string='Salesman Group', )
