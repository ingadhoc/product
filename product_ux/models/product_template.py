##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductTemplate(models.Model):
<<<<<<< 13e2d2f1c2fb0d8925efc0d6a663966c20d7dd12
    _name = "product.template"
    _inherit = ["product.template", "product.search.mixin"]
||||||| 20a98de6f8dababd58d0de573b0e41da633d2dc3
    _inherit = "product.template"
=======
    _name = "product.template"
    _inherit = ["product.template", "product.search.mixin"]

    # the template keeps no code when it has several variants
    _search_native_paths = ("name", "product_variant_ids.default_code")
>>>>>>> 2dd56d98370fcab6b829592dd1b7b8048841e3b5

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
        Basicamente esto de acá https://github.com/odoo/odoo/blob/13.0/addons/product/models/product_template.py#L213
        Si viene lista obtenemos el primer elemento
        Luego, si ese elemento es string buscamos a traves de name search.
        Para otros casos devolvemos super (debería ser un ID)
        """
        pricelist_id_or_name = self.env.context.get("pricelist")
        if isinstance(pricelist_id_or_name, list):
            pricelist_id_or_name = pricelist_id_or_name[0]
            # Si viene una lista en pricelist actualizamos contexto para que si se llama super, este reciba un entero
            self = self.with_context(pricelist=pricelist_id_or_name)
        if isinstance(pricelist_id_or_name, str):
            pricelist_data = self.env["product.pricelist"].name_search(pricelist_id_or_name, operator="=", limit=1)
            if pricelist_data:
                return self.env["product.pricelist"].browse(pricelist_data[0][0])
            else:
                return self.env["product.pricelist"]
        return super()._get_contextual_pricelist()
<<<<<<< 13e2d2f1c2fb0d8925efc0d6a663966c20d7dd12

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        results = super().name_search(name, domain, operator, limit)
        return self._extend_name_search(results, name, domain, operator, limit)
||||||| 20a98de6f8dababd58d0de573b0e41da633d2dc3
=======

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        results = super().name_search(name, args, operator, limit)
        return self._extend_name_search(results, name, args, operator, limit)
>>>>>>> 2dd56d98370fcab6b829592dd1b7b8048841e3b5
