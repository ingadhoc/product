##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    active = fields.Boolean(tracking=True)
    sellers_product_code = fields.Char(
        'Vendor Product Code',
        related='seller_ids.product_code',
    )
    warranty = fields.Float()
    pricelist_price = fields.Float(compute='_compute_product_pricelist_price', digits='Product Price')
    odumbo_price = fields.Float(compute='_compute_product_odumbo_price', digits='Product Price')
    pricelist_id = fields.Many2one('product.pricelist', store=False,)

    @api.depends_context('pricelist', 'quantity', 'uom', 'date', 'no_variant_attributes_price_extra')
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()

    @api.depends_context('pricelist', 'quantity', 'uom', 'date', 'no_variant_attributes_price_extra')
    def _compute_product_odumbo_price(self):
        for record in self:
            company_id = self._context.get('company_id', self.env.company.id)
            price = record._get_contextual_price()
            res = record.taxes_id.filtered(lambda x: x.company_id.id == company_id).compute_all(price, product=record)
            record.odumbo_price = res['total_included']
