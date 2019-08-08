from odoo import fields, models


class Uom(models.Model):
    _inherit = 'uom.uom'

    description = fields.Char(
    )
