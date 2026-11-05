##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ProductCatalogLineMixin(models.AbstractModel):
    _inherit = "product.catalog.line.mixin"

    def _catalog_qty(self, catalog_uom):
        """Quantity of this line the way the catalog sums it: the stored quantity
        field of the model, in the catalog unit."""
        self.ensure_one()
        return self._get_product_uom()._compute_quantity(qty=self[self._get_quantity_field()], to_unit=catalog_uom)

    def _set_catalog_qty(self, quantity, catalog_uom):
        """Store on this line a quantity given in the catalog unit, keeping the
        unit of the line."""
        self.ensure_one()
        self[self._get_quantity_field()] = catalog_uom._compute_quantity(qty=quantity, to_unit=self._get_product_uom())
