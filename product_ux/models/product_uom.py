from odoo import fields, models


class ProductUoM(models.Model):
    _inherit = 'product.uom'

    description = fields.Char(
    )
