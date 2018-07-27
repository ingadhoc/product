##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    price = fields.Monetary(
        compute='_compute_price',
        help='Price for product specified on the context',
    )
    show_products = fields.Boolean(
        'Show in products',
        default=True,
        help="By selecting it allows you to display the pricelist "
        "with the price of that product in the products",
    )

    @api.multi
    def _compute_price(self):
        product_id = self._context.get('product_id', False)
        template_id = self._context.get('template_id', False)
        for rec in self:
            if product_id:
                price = self.env['product.product'].browse(
                    product_id).with_context(pricelist=rec.id).price
                rec.price = price
            elif template_id:
                price = self.env['product.template'].browse(
                    template_id).with_context(pricelist=rec.id).price
                rec.price = price
