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
    warranty = fields.Float(help="Informative field to define the warranty months of the product. Do not have relation with other models.")
    pricelist_price = fields.Float(compute='_compute_product_pricelist_price', digits='Product Price')
    pricelist_id = fields.Many2one('product.pricelist', store=False,)

    @api.depends_context('pricelist', 'quantity', 'uom', 'date', 'no_variant_attributes_price_extra')
    def _compute_product_pricelist_price(self):
        context = dict(self._context)
        if 'pricelist' in context:
            id_pricelist = next((x for x in context['pricelist'] if isinstance(x, int)), None)
            if id_pricelist is None:
                pricelist_name_search = self.env['product.pricelist'].name_search(
                        context['pricelist'][0], operator="ilike", limit=1
                    )
                context['pricelist'] = pricelist_name_search[0][0] if pricelist_name_search else False
            else:
                context['pricelist'] = id_pricelist
        for product in self:
            product.pricelist_price = product.with_context(context)._get_contextual_price()
