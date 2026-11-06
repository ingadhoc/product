##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # name it _lst_price and not list_price because on product.product
    # we want to extend prices for lst_price (on product template list_price
    # and lst_price are the same)
    taxed_lst_price = fields.Float(
        string="Taxed Sale Price",
        compute="_compute_taxed_lst_price",
        digits="Product Price",
        compute_sudo=True,
    )

    @api.depends("taxes_id", "list_price")
    @api.depends_context("company", "company_id")
    def _compute_taxed_lst_price(self):
        """compute it from list_price and not for lst_price for performance
        (avoid using dummy related field)
        """
        company = self.env["res.company"].browse(self.env.context.get("company_id")) or self.env.company
        for product in self:
            product.taxed_lst_price = product.taxes_id._filter_taxes_by_company(company).compute_all(
                product.list_price, self.env.company.currency_id, product=product
            )["total_included"]

    @api.depends_context("taxes_included")
    def _compute_product_pricelist_price(self):
        return super()._compute_product_pricelist_price()
