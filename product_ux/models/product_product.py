##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    active = fields.Boolean(tracking=True)
    pricelist_price = fields.Float(compute='_compute_product_pricelist_price', digits='Product Price')
    product_catalog_qty = fields.Float(
        string="Quantity",
        compute='_compute_catalog_values',
        inverse='_inverse_catalog_values',
    )
    product_catalog_price = fields.Float(
        string="Price",
        compute='_compute_catalog_values',
        readonly=True,
    )

    @api.depends_context('pricelist', 'quantity', 'uom', 'date', 'no_variant_attributes_price_extra')
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()

    @api.depends_context('product_catalog_order_model', 'order_id')
    def _compute_catalog_values(self):
        res_model = self._context.get('product_catalog_order_model')
        order_id = self._context.get('order_id')
        order = self.env[res_model].browse(order_id)
        order_line_info = order.with_company(order.company_id)._get_product_catalog_order_line_info(product_ids=self.ids)
        for rec in self:
            rec.product_catalog_qty = order_line_info[rec.id].get('quantity')
            rec.product_catalog_price = order_line_info[rec.id].get('price')

    def _inverse_catalog_values(self):
        res_model = self._context.get('product_catalog_order_model')
        order_id = self._context.get('order_id')
        order = self.env[res_model].browse(order_id)
        for rec in self:
            order.with_company(order.company_id)._update_order_line_info(rec.id, rec.product_catalog_qty)

    def increase_quantity(self):
        for rec in self:
            rec.product_catalog_qty += 1
