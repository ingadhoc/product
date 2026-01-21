##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductCatalog(models.TransientModel):
    _name = "product.product_catalog.wizard"
    _description = "Wizard to generate the Product Catalog Report with Aeroo"

    product_catalog_report_id = fields.Many2one(
        "product.product_catalog_report",
        "Product Catalog",
        required=True,
    )
    taxes_included = fields.Boolean()
    use_planned_price = fields.Boolean(
        help="Use planned price instead of list price (if planned price module"
        " is not installed, nothing is going to change)",
    )
    product_count = fields.Integer("Cantidad de productos", compute="compute_estimated_info", store=True)
    pricelist_count = fields.Integer("Cantidad de listas", compute="compute_estimated_info", store=True)
    estimated_time = fields.Char("Tiempo estimado", compute="compute_estimated_info", store=True)

    @api.onchange("product_catalog_report_id")
    def change_product_catalog_report(self):
        self.taxes_included = self.product_catalog_report_id.taxes_included

    def generate_report(self):
        self.ensure_one()
        return self.product_catalog_report_id.with_context(
            taxes_included=self.taxes_included, use_planned_price=self.use_planned_price
        ).generate_report()

    @api.onchange("product_catalog_report_id")
    def compute_estimated_info(self):
        def format_time(seconds):
            if seconds < 60:
                return "menos de 1 minuto"
            elif seconds < 120:
                return "más de 1 minuto"
            elif seconds < 180:
                return "más de 2 minutos"
            elif seconds < 240:
                return "más de 3 minutos"
            elif seconds < 300:
                return "más de 4 minutos"
            else:
                return "más de 5 minutos"

        for rec in self:
            report = rec.product_catalog_report_id

            if report.category_type == "public_category":
                public_categories = report.public_category_ids
                if report.include_sub_categories and public_categories:
                    public_categories = report.env["product.public.category"].search(
                        [("id", "child_of", public_categories.ids)]
                    )
                productos_publicos = self.env["product.template"].search_count(
                    [("public_categ_ids", "in", public_categories.ids)]
                )
                rec.product_count = productos_publicos

                # Estimación ajustada para públicas
                TIEMPO_POR_PRODUCTO_PUBLIC = 0.0495
                tiempo_total = productos_publicos * TIEMPO_POR_PRODUCTO_PUBLIC
                rec.estimated_time = format_time(tiempo_total)

            else:
                categories = report.category_ids
                if report.include_sub_categories and categories:
                    categories = report.env["product.category"].search([("id", "child_of", categories.ids)])
                productos_internos = self.env["product.template"].search_count([("categ_id", "in", categories.ids)])
                rec.product_count = productos_internos

                # Estimación ajustada para internas
                TIEMPO_POR_PRODUCTO_INTERNAL = 0.00825
                tiempo_total = productos_internos * TIEMPO_POR_PRODUCTO_INTERNAL
                rec.estimated_time = format_time(tiempo_total)
