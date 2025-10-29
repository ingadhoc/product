##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_uoms(self, product_uom, use=False):
        """
        if product has uoms configured, we use them
        if not, we choose all uoms from uom_id category (first the product uom)
        We send product uom so it can be send from sale or purchase
        """
        self.ensure_one()
        # Get the root reference UoM by traversing up the parent chain
        root_uom = product_uom
        while root_uom.relative_uom_id:
            root_uom = root_uom.relative_uom_id

        # Find all UoMs that have the same root reference
        all_uoms = self.env["uom.uom"].search([])
        compatible_uoms = all_uoms.filtered(lambda u: u._has_common_reference(product_uom) and u.id != product_uom.id)

        return product_uom + compatible_uoms
