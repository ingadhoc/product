##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductCatalog(models.TransientModel):
    _name = "product.product_catalog.wizard"
    _description = "Wizard to generate the Product Catalog Report"

    product_catalog_report_id = fields.Many2one(
        "product.product_catalog_report",
        "Product Catalog",
        required=True,
        help="Select the catalog configuration to use. Each catalog defines its categories, pricelists, and report format.",
    )
    taxes_included = fields.Boolean(
        help="When enabled, prices will include applicable taxes.",
    )
    use_planned_price = fields.Boolean(
        help="Use planned price instead of list price (has no effect if the planned price module is not installed).",
    )

    @api.onchange("product_catalog_report_id")
    def change_product_catalog_report(self):
        self.taxes_included = self.product_catalog_report_id.taxes_included

    def generate_report(self):
        self.ensure_one()
        return self.product_catalog_report_id.with_context(
            taxes_included=self.taxes_included, use_planned_price=self.use_planned_price
        ).generate_report()
