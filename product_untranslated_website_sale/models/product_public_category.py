from odoo import models, fields


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    name = fields.Char(translate=False)
