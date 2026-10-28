##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_product_catalog_product_data(self, product, **kwargs):
        res = super()._get_product_catalog_product_data(product, **kwargs)
        allowed_uoms = product._get_purchase_uoms()
        if "availableUoms" in res and allowed_uoms and res["uomId"] not in allowed_uoms.ids:
            uom = allowed_uoms[:1]
            res.update(self._get_product_catalog_uom_data(product, uom, **kwargs))
            if self._show_prices():
                res["price"] = self._get_product_catalog_default_unit_price(product, uom, **kwargs)
        return res

    def _get_product_catalog_uom_data(self, product, uom, **kwargs):
        res = super()._get_product_catalog_uom_data(product, uom, **kwargs)
        allowed_uoms = product._get_purchase_uoms()
        if "availableUoms" in res and allowed_uoms:
            # keep the current UoM, as the core does, so an existing line still shows it
            res["availableUoms"] = (allowed_uoms | uom).read(["name", "factor"])
        return res
