##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_catalog_price_taxed = fields.Float(
        string="Order Price with Taxes",
        compute="_compute_product_catalog_price_taxed",
        readonly=True,
    )

    def _get_catalog_order(self):
        """Return the order record from context, or None."""
        res_model = self.env.context.get("product_catalog_order_model")
        order_id = self.env.context.get("order_id")
        if not res_model or not order_id:
            return None
        order = self.env[res_model].browse(order_id)
        return order if order.exists() else None

    @api.depends("product_tmpl_id.taxes_id")
    @api.depends_context("company", "company_id", "order_id", "product_catalog_order_model")
    def _compute_product_catalog_price_taxed(self):
        order = self._get_catalog_order()
        company_id = self.env.context.get("company_id", self.env.company.id)

        for rec in self:
            price = rec.product_catalog_price
            if not price:
                rec.product_catalog_price_taxed = 0.0
                continue

            currency = self.env.company.currency_id
            partner = self.env["res.partner"]
            taxes = rec.taxes_id.filtered(lambda x: x.company_id.id == company_id)

            if order:
                currency = order.currency_id or currency
                partner = order.partner_id
                company_id = (order.company_id or self.env.company).id
                taxes = rec.taxes_id.filtered(lambda x: x.company_id.id == company_id)
                if order.fiscal_position_id:
                    taxes = order.fiscal_position_id.map_tax(taxes)

            tax_result = taxes.sudo().compute_all(price, currency=currency, quantity=1.0, product=rec, partner=partner)
            rec.product_catalog_price_taxed = tax_result["total_included"]
