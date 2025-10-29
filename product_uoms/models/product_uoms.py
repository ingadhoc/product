##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductUoms(models.Model):
    _name = "product.uoms"
    _description = "Product Uoms"
    _order = "sequence"

    sequence = fields.Integer(
        default=10,
    )
    product_tmpl_id = fields.Many2one("product.template", string="Product Template")
    uom_id = fields.Many2one(
        "uom.uom",
        string="UOM",
        required=True,
    )

    _uom_uniq = models.Constraint(
        "unique(product_tmpl_id, uom_id)",
        "UOM must be unique per Product Template!",
    )
