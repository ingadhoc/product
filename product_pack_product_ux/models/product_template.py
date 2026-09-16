##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _get_catalog_order(self):
        res_model = self.env.context.get("product_catalog_order_model")
        res_id = self.env.context.get("product_catalog_order_id") or self.env.context.get("order_id")
        if not res_model or not res_id or res_model not in self.env:
            return None
        return self.env[res_model].browse(res_id).exists()

    @api.model
    def _get_pack_pricelist_price_context(self):
        ctx = {"whole_pack_price": True}
        order = self._get_catalog_order()
        if order is None:
            return ctx
        if not self.env.context.get("pricelist") and order._fields.get("pricelist_id") and order.pricelist_id:
            ctx["pricelist"] = order.pricelist_id.id
        if not self.env.context.get("date") and order._fields.get("date_order") and order.date_order:
            ctx["date"] = order.date_order
        return ctx

    @api.depends_context("product_catalog_order_model", "product_catalog_order_id", "order_id")
    def _compute_product_pricelist_price(self):
        records = self.with_context(**self._get_pack_pricelist_price_context())
        super(ProductTemplate, records)._compute_product_pricelist_price()
        for product, record in zip(self, records):
            product.pricelist_price = record.pricelist_price
