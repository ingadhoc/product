##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    uom_po_ids = fields.Many2many(
        "uom.uom",
        "product_template_uom_po_rel",
        "product_tmpl_id",
        "uom_id",
        string="Purchase Packagings",
        help="Additional packagings for this product which can be used for purchase",
        domain="[('id', '!=', uom_id)]",
    )

    use_product_uom = fields.Boolean(
        default=True,
        help="When enabled, it allows to use the product uom in the purchase order.",
    )
