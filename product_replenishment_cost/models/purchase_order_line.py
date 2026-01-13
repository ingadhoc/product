##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("product_qty", "product_uom_id")
    def _compute_price_unit_and_date_planned_and_name(self):
        super()._compute_price_unit_and_date_planned_and_name()

        for line in self:
            # Skip if manually modified (Odoo way: technical_price_unit != price_unit)
            if not line.product_id or (line.technical_price_unit != line.price_unit):
                continue

            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date(),
                uom_id=line.product_uom_id,
            )

            if not seller:
                continue

            price_unit = (
                line.env["account.tax"]._fix_tax_included_price_company(
                    seller.net_price, line.product_id.supplier_taxes_id, line.tax_ids, line.company_id
                )
                if seller
                else 0.0
            )
            price_unit = seller.currency_id._convert(
                price_unit, line.currency_id, line.company_id, line.date_order or fields.Date.today()
            )

            if seller and line.product_uom_id and seller.product_uom_id != line.product_uom_id:
                price_unit = seller.product_uom_id._compute_price(price_unit, line.product_uom_id)

            # Update both price_unit and technical_price_unit
            line.price_unit = line.technical_price_unit = price_unit

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
        # Para casos como cuando se viene de reabastecimientos, usamos el nuevo net_price en vez de price
        res = super()._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, supplier, po)

        # Check if supplier is a product.supplierinfo or res.partner
        # When called from procurement, supplier is res.partner (supplier.partner_id from core)
        # When called directly, supplier is product.supplierinfo
        if supplier and supplier._name == "product.supplierinfo":
            price_unit = (
                self.env["account.tax"]._fix_tax_included_price_company(
                    supplier.net_price, product_id.supplier_taxes_id, self.tax_ids, company_id
                )
                if supplier
                else 0.0
            )
            if price_unit and supplier and po.currency_id and supplier.currency_id != po.currency_id:
                price_unit = supplier.currency_id._convert(
                    price_unit, po.currency_id, po.company_id, po.date_order or fields.Date.today()
                )
            res["price_unit"] = price_unit

        return res
