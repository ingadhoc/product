from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name = fields.Char(translate=False)
