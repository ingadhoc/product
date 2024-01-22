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
        for product in self:
            product.pricelist_price = product._get_contextual_price()

    def _get_contextual_pricelist(self):
        """ Re agregamos compatibilidad con que la lista de precios se mande como name o como lista en el contexto
        Basicamente esto de acá https://github.com/odoo/odoo/blob/13.0/addons/product/models/product_template.py#L213
        Si viene lista obtenemos el primer elemento
        Luego, si ese elemento es string buscamos a traves de name search.
        Para otros casos devolvemos super (debería ser un ID)
        """
        pricelist_id_or_name = self._context.get('pricelist')
        if isinstance(pricelist_id_or_name, list):
            pricelist_id_or_name = pricelist_id_or_name[0]
        if isinstance(pricelist_id_or_name, str):
            pricelist_data = self.env['product.pricelist'].name_search(pricelist_id_or_name, operator='ilike', limit=1)
            if pricelist_data:
                return self.env['product.pricelist'].browse(pricelist_data[0][0])
            else:
                return self.env['product.pricelist']
        return super()._get_contextual_pricelist()
