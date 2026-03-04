##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):
        """Invalida el caché del catálogo de productos cuando cambian los impuestos en líneas de orden."""
        # Guardar impuestos antiguos para comparar
        old_taxes_map = {line.id: line.tax_ids.ids for line in self}
        res = super().write(vals)

        if "tax_ids" in vals:
            # Verificar qué líneas realmente cambiaron los impuestos
            changed_lines = self.filtered(lambda l: old_taxes_map.get(l.id) != l.tax_ids.ids)
            if changed_lines:
                products = changed_lines.mapped("product_id")
                if products:
                    # Invalidar caché y marcar como modificado para forzar recálculo
                    products.invalidate_recordset(["product_catalog_price_taxed"])
                    products.modified(["product_catalog_price_taxed"])
        return res
