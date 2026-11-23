##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    sequence = fields.Integer()
    pricelist_allowed_ids = fields.Many2many(
        comodel_name="product.pricelist",
        relation="product_pricelist_allowed_rel",
        column1="pricelist_id",
        column2="allowed_pricelist_id",
        string="Allowed Pricelists",
        help="Pricelists that a user with price restriction can select",
    )
