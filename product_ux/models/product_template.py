##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    active = fields.Boolean(tracking=True)
    sellers_product_code = fields.Char(
        "Vendor Product Code",
        related="seller_ids.product_code",
    )
    warranty = fields.Float(
        help="Informative field to define the warranty months of the product. Do not have relation with other models."
    )
    pricelist_price = fields.Float(compute="_compute_product_pricelist_price", digits="Product Price")
    pricelist_id = fields.Many2one(
        "product.pricelist",
        store=False,
    )

    @api.depends_context("pricelist", "quantity", "uom", "date", "no_variant_attributes_price_extra")
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()

    def _get_contextual_pricelist(self):
        """Re agregamos compatibilidad con que la lista de precios se mande como name o como lista en el contexto
        (la vista de búsqueda manda lo que escribe el usuario), como hasta 13.0:
        https://github.com/odoo/odoo/blob/13.0/addons/product/models/product_template.py#L213
        Si viene lista tomamos el primer elemento; si es string, la buscamos por nombre.
        Para otros casos devolvemos super (debería ser un ID).
        """
        pricelist = self.env.context.get("pricelist")
        if isinstance(pricelist, list):
            pricelist = pricelist and pricelist[0]
            # super espera un entero en el contexto
            self = self.with_context(pricelist=pricelist)
        if isinstance(pricelist, str):
            found = self.env["product.pricelist"].name_search(pricelist, operator="=", limit=1)
            return self.env["product.pricelist"].browse(found and found[0][0])
        return super()._get_contextual_pricelist()
