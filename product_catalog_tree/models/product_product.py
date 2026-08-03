##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import json

from lxml import etree
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_catalog_qty = fields.Float(
        string="Quantity",
        compute="_compute_catalog_values",
    )
    product_catalog_price = fields.Float(
        string="Order Price",
        compute="_compute_catalog_values",
        readonly=True,
    )
    product_catalog_min_qty = fields.Float(
        string="Supplier Min Qty",
        compute="_compute_catalog_values",
        readonly=True,
    )

    def write(self, vals):
        """
        Si en vals solo viene product_catalog_qty hacemos esto para que usuarios sin permiso de escribir
        en productos puedan modificar la cantidad
        """
        if len(vals) == 1 and "product_catalog_qty" in vals:
            qty = vals.get("product_catalog_qty")
            self._inverse_catalog_values(qty)
            return True
        return super().write(vals)

    def _compute_catalog_values(self):
        res_model = self._context.get("product_catalog_order_model")
        order_id = self._context.get("order_id")

        if not res_model or not order_id:
            self.product_catalog_qty = 0
            self.product_catalog_price = 0
            self.product_catalog_min_qty = 0
            return

        order = self.env[res_model].browse(order_id)
        order_line_info = order.with_company(order.company_id)._get_product_catalog_order_line_info(
            product_ids=self.ids
        )
        for rec in self:
            rec.product_catalog_qty = order_line_info[rec.id].get("quantity")
            rec.product_catalog_price = order_line_info[rec.id].get("price")
            rec.product_catalog_min_qty = order_line_info[rec.id].get("min_qty", 0)

    def _inverse_catalog_values(self, product_catalog_qty):
        res_model = self._context.get("product_catalog_order_model")
        order_id = self._context.get("order_id")

        if not res_model or not order_id:
            return

        order = self.env[res_model].browse(order_id)
        # Distintos modelos de orden (sale.order, purchase.order, account.move,
        # repair.order, ...) exponen sus líneas con nombres de campo distintos, por
        # lo que usamos el hook estándar del catálogo de productos en lugar de
        # asumir "order_line" (repair.order, por ejemplo, no lo tiene).
        qty_field = "quantity" if res_model == "account.move" else "product_uom_qty"
        record_lines = order._get_product_catalog_record_lines(self.ids)
        for rec in self:
            existing_lines = record_lines[rec]
            if len(existing_lines) > 1 and product_catalog_qty > 0:
                total_current_qty = sum(existing_lines.mapped(qty_field))
                qty_difference = product_catalog_qty - total_current_qty
                if qty_difference >= 0:
                    setattr(existing_lines[0], qty_field, getattr(existing_lines[0], qty_field) + qty_difference)
                else:
                    remaining_to_reduce = abs(qty_difference)
                    for line in existing_lines:
                        if remaining_to_reduce <= 0:
                            break
                        current_qty = getattr(line, qty_field)
                        can_reduce = min(current_qty, remaining_to_reduce)
                        setattr(line, qty_field, current_qty - can_reduce)
                        remaining_to_reduce -= can_reduce
            else:
                # Actualizar la información de la línea de orden
                # Call the order method with a cleared context to avoid errors on creating move line
                order = order.with_env(self.env(context={})).with_company(order.company_id)
                order._update_order_line_info(rec.id, product_catalog_qty)

    def increase_quantity(self):
        for rec in self:
            rec._inverse_catalog_values(rec.product_catalog_qty + 1)

    def set_catalog_min_qty(self):
        """Set the order quantity to the vendor's minimum quantity.

        The list catalog ``+`` button (:meth:`increase_quantity`) always adds
        one unit, so a line can stay below the vendor ``min_qty`` and fall back
        to the product cost instead of the vendor pricelist price. This
        dedicated button always sets the quantity to the vendor ``min_qty`` --
        whether the product is already on the order or not -- so the vendor
        price applies. The button is only shown when the vendor defines a
        ``min_qty`` greater than 1.
        """
        for rec in self:
            if rec.product_catalog_min_qty:
                rec._inverse_catalog_values(rec.product_catalog_min_qty)

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        If we came from invoice, we send in context 'force_line_edit'
        and we change list view to make editable and also field qty
        """
        res = super().get_view(view_id=view_id, view_type=view_type, **options)

        catalog_tree_view_id = self.env.ref("product_catalog_tree.product_view_tree_catalog").id

        if view_id and view_id == catalog_tree_view_id:
            doc = etree.XML(res["arch"])

            # make all fields not editable
            for node in doc.xpath("//field"):
                node.set("readonly", "1")
                modifiers = json.loads(node.get("modifiers") or "{}")
                modifiers["readonly"] = True
                node.set("modifiers", json.dumps(modifiers))

            # make qty field editable
            qty_field = doc.xpath("//field[@name='product_catalog_qty']")[0]
            qty_field.set("readonly", "false")

            for node in doc.xpath("/list"):
                node.set("edit", "true")
                node.set("create", "false")
                node.set("editable", "top")

            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
