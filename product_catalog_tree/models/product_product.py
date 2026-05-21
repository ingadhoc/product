##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import json
import logging

from lxml import etree
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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
    product_catalog_supplier_uom = fields.Char(
        string="Supplier UoM",
        compute="_compute_catalog_supplier_uom",
        readonly=True,
    )
    product_catalog_price_taxed = fields.Float(
        string="Order Price with taxes",
        compute="_compute_product_catalog_price_taxed",
        readonly=True,
    )

    def _get_order_context_data(self):
        res_model = self.env.context.get("product_catalog_order_model")
        order_id = self.env.context.get("order_id")
        if not res_model or not order_id:
            return None
        order = self.env[res_model].browse(order_id)
        return order if order.exists() else None

    def _compute_catalog_supplier_uom(self):
        res_model = self.env.context.get("product_catalog_order_model")
        order = self._get_order_context_data()

        for rec in self:
            rec.product_catalog_supplier_uom = ""
            if res_model == "purchase.order" and order and order.partner_id:
                seller = rec.seller_ids.filtered(lambda s: s.partner_id == order.partner_id)[:1]
                if seller and seller.product_uom_id:
                    rec.product_catalog_supplier_uom = seller.product_uom_id.name

    @api.depends("product_tmpl_id.taxes_id", "product_catalog_price")
    @api.depends_context("company", "company_id", "order_id", "product_catalog_order_model")
    def _compute_product_catalog_price_taxed(self):
        order = self._get_order_context_data()

        for rec in self:
            if not rec.product_catalog_price:
                rec.product_catalog_price_taxed = 0.0
                continue

            currency = self.env.company.currency_id
            partner = self.env["res.partner"]
            company_id = self.env.context.get("company_id", self.env.company.id)
            taxes = rec.taxes_id.filtered(lambda x: x.company_id.id == company_id)

            if order:
                currency = order.currency_id or currency
                partner = order.partner_id
                company_id = (order.company_id or self.env.company).id
                taxes = rec.taxes_id.filtered(lambda x: x.company_id.id == company_id)
                if order.fiscal_position_id:
                    taxes = order.fiscal_position_id.map_tax(taxes)

            if taxes:
                try:
                    tax_result = taxes.sudo().compute_all(
                        rec.product_catalog_price, currency=currency, quantity=1.0, product=rec, partner=partner
                    )
                    rec.product_catalog_price_taxed = tax_result["total_included"]
                except Exception:
                    _logger.warning(
                        "Failed to compute taxed price for product %s, falling back to base price",
                        rec.id,
                        exc_info=True,
                    )
                    rec.product_catalog_price_taxed = rec.product_catalog_price
            else:
                rec.product_catalog_price_taxed = rec.product_catalog_price

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
        res_model = self.env.context.get("product_catalog_order_model")
        order_id = self.env.context.get("order_id")

        if not res_model or not order_id:
            self.product_catalog_qty = 0
            self.product_catalog_price = 0
            return

        order = self.env[res_model].browse(order_id)
        order_line_info = order.with_company(order.company_id)._get_product_catalog_order_line_info(
            product_ids=self.ids
        )
        for rec in self:
            rec.product_catalog_qty = order_line_info[rec.id].get("quantity")
            rec.product_catalog_price = order_line_info[rec.id].get("price")

    def _inverse_catalog_values(self, product_catalog_qty):
        res_model = self.env.context.get("product_catalog_order_model")
        order_id = self.env.context.get("order_id")

        if not res_model or not order_id:
            return

        order = self.env[res_model].browse(order_id)

        for rec in self:
            if res_model == "account.move":
                existing_lines = order.invoice_line_ids.filtered(lambda line: line.product_id.id == rec.id)
            else:
                existing_lines = order.order_line.filtered(lambda line: line.product_id.id == rec.id)
            if len(existing_lines) > 1 and product_catalog_qty > 0:
                total_current_qty = sum(existing_lines.mapped("product_uom_qty"))
                qty_difference = product_catalog_qty - total_current_qty
                if qty_difference >= 0:
                    existing_lines[0].product_uom_qty += qty_difference
                else:
                    remaining_to_reduce = abs(qty_difference)
                    for line in existing_lines:
                        if remaining_to_reduce <= 0:
                            break
                        can_reduce = min(line.product_uom_qty, remaining_to_reduce)
                        line.product_uom_qty -= can_reduce
                        remaining_to_reduce -= can_reduce
            else:
                # Actualizar la información de la línea de orden
                # Call the order method with a cleared context to avoid errors on creating move line
                minimal_context = {
                    "lang": self._context.get("lang"),
                    "tz": self._context.get("tz"),
                    "uid": self._context.get("uid"),
                    "allowed_company_ids": self._context.get("allowed_company_ids"),
                }
                order.with_company(order.company_id).with_env(
                    self.env(context=minimal_context)
                )._update_order_line_info(rec.id, product_catalog_qty)

    def increase_quantity(self):
        for rec in self:
            rec._inverse_catalog_values(rec.product_catalog_qty + 1)

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
