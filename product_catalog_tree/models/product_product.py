##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from lxml import etree


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_catalog_qty = fields.Float(
        string="Quantity",
        compute='_compute_catalog_values',
        inverse='_inverse_catalog_values',
    )
    product_catalog_price = fields.Float(
        string="Order Price",
        compute='_compute_catalog_values',
        readonly=True,
    )

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

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """
        If we came from invoice, we send in context 'force_line_edit'
        and we change list view to make editable and also field qty
        """
        res = super().get_view(
            view_id=view_id, view_type=view_type, **options)

        catalog_tree_view_id = self.env.ref('product_catalog_tree.product_view_tree_catalog').id

        if view_id and view_id == catalog_tree_view_id and view_type == 'tree':
            doc = etree.XML(res['arch'])

            # make all fields not editable
            for node in doc.xpath("//field"):
                node.set('readonly', '1')

            qty_field = doc.xpath("//field[@name='product_catalog_qty']")[0]
            qty_field.set('readonly', 'false')

            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
