##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_purchase_uoms(self):
        """UoMs allowed to purchase this product: its purchase packagings, the vendor
        UoMs and, if use_product_uom is set, the product UoM.
        """
        self.ensure_one()
        uoms = self.uom_po_ids | self.seller_ids.mapped("uom_id")
        if self.use_product_uom:
            uoms = self.uom_id | uoms
        return uoms
