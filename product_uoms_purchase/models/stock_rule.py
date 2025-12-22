##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        """We modify this method to set the correct UoM based on the product's
        use_product_uom configuration and available purchase UoMs.

        Logic:
        - If use_product_uom is True: allow product UoM, purchase UoMs, and supplier UoMs
        - If use_product_uom is False: only allow purchase UoMs and supplier UoMs
        """
        res = super()._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)

        supplier_uoms = product_id.seller_ids.mapped("product_uom_id")

        if product_id.product_tmpl_id.use_product_uom:
            allowed_uoms = product_id.uom_id | product_id.uom_po_ids | supplier_uoms
        else:
            allowed_uoms = product_id.uom_po_ids | supplier_uoms

        if allowed_uoms and product_uom not in allowed_uoms:
            res["product_uom"] = allowed_uoms[0].id

        return res
