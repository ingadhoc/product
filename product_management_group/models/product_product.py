from odoo import models, api
import json


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        # Hacemos esto para evitar la edición desde la vista form de productos cuando se accede desde el botón 
        # "Search Products" en ventas y compras.
        arch, view = super()._get_view(view_id, view_type, **options)
        if ((self._context.get('sale_quotation_products') or self._context.get('purchase_quotation_products'))
            and view_type == 'form' and not self.env.user.has_group('product_management_group.group_products_management')):
                for node in arch.xpath("//field[@name]"):
                    node.set('readonly', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
