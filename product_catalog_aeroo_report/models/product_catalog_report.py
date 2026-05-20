##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, fields, models
from odoo.tools import formatLang


class ProductCatalogReport(models.Model):
    _name = "product.product_catalog_report"
    _description = "Product Catalog Report"

    name = fields.Char(
        required=True,
    )
    products_order = fields.Char(
        "Products Order Sintax",
        help="Order expression for products (e.g. 'name asc', 'default_code'). Leave empty to use default order.",
        required=False,
    )
    categories_order = fields.Char(
        "Categories Order Sintax",
        help="Order expression for categories (e.g. 'name asc', 'sequence desc'). Leave empty to use default order.",
    )
    include_sub_categories = fields.Boolean(
        "Include Subcategories?",
        help="If enabled, products from all subcategories of the selected categories will also be included.",
    )
    only_with_stock = fields.Boolean(
        "Only With Stock Products?",
        help="If enabled, only products with available stock will be included in the catalog.",
    )
    taxes_included = fields.Boolean(
        "Taxes Included?",
        help="When enabled, prices will include applicable taxes. This value is used as default when printing.",
    )
    print_product_uom = fields.Boolean(
        "Print Product UOM?",
        help="If enabled, the unit of measure is printed next to each product name.",
    )
    product_type = fields.Selection(
        [("product.template", "Product Template"), ("product.product", "Product")],
        required=True,
        help="Choose whether the catalog is based on product templates (variants grouped) or individual product variants.",
    )
    prod_display_type = fields.Selection(
        [
            ("prod_per_line", "One Product Per Line"),
            ("prod_list", "Product List"),
            ("variants", "Variants"),
        ],
        "Product Display Type",
        help="Controls how variants appear in the report: one per line lists each variant separately, "
        "product list shows a summary, variants shows attributes.",
    )
    report_id = fields.Many2one(
        "ir.actions.report",
        string="Report",
        domain=[("report_type", "in", ["qweb-pdf", "qweb-html"]), ("model", "=", "product.product_catalog_report")],
        context={"default_report_type": "qweb-pdf", "default_model": "product.product_catalog_report"},
        required=True,
        help="Select the report format to use when printing this catalog (PDF simple, PDF by categories, or XLSX export).",
    )
    category_ids = fields.Many2many(
        "product.category",
        "product_catalog_report_categories",
        "product_catalog_report_id",
        "category_id",
        "Product Categories",
        help="Filter the catalog to products from these categories. Leave empty to include all categories.",
    )
    pricelist_ids = fields.Many2many(
        "product.pricelist",
        "product_catalog_report_pricelists",
        "product_catalog_report_id",
        "pricelist_id",
        "Pricelist",
        help="Select the pricelists whose prices will appear as columns in the catalog.",
    )

    category_type = fields.Selection(
        [("product_category", "Product Category")],
        default="product_category",
        required=True,
    )

    def prepare_report(self):
        context = dict(self.env.context.copy())
        categories = self.category_ids
        # because this value usually cames from wizard, if we call report from
        # this model, we add taxes_included parameter
        if "taxes_included" not in context:
            context.update({"taxes_included": self.taxes_included})
        if self.include_sub_categories and categories:
            categories = self.env["product.category"].search([("id", "child_of", categories.ids)])
        context.update(
            {
                "category_ids": categories.ids,
                "product_type": self.product_type,
                "pricelist_ids": self.pricelist_ids.ids,
                "products_order": self.products_order,
                "categories_order": self.categories_order,
                "only_with_stock": self.only_with_stock,
                "prod_display_type": self.prod_display_type,
                "print_product_uom": self.print_product_uom,
                "category_type": self.category_type,
            }
        )
        return self.with_context(**context)

    def get_categories(self):
        self.ensure_one()
        category_model = "product.public.category" if self.category_type == "public_category" else "product.category"
        categories = self.category_ids
        if self.include_sub_categories and categories:
            categories = self.env[category_model].search([("id", "child_of", categories.ids)])
        if not categories:
            return self.env[category_model]
        return self.env[category_model].search([("id", "in", categories.ids)], order=self.categories_order or "id")

    def get_products(self, category_ids):
        self.ensure_one()
        if hasattr(category_ids, "ids"):
            category_ids = category_ids.ids
        elif not isinstance(category_ids, list):
            category_ids = [category_ids]
        order = self.products_order or "id"
        if self.category_type == "public_category":
            domain = [("public_categ_ids", "in", category_ids)]
        else:
            domain = [("categ_id", "in", category_ids)]
        if self.only_with_stock:
            domain.append(("qty_available", ">", 0))
        return self.env[self.product_type].search(domain, order=order)

    def get_report_products(self, category):
        self.ensure_one()
        return self.get_products(category)

    def get_all_products(self):
        self.ensure_one()
        categories = self.get_categories()
        if not categories:
            return self.env[self.product_type]
        return self.get_products(categories)

    def get_variant_details(self, product):
        self.ensure_one()
        if self.product_type != "product.template":
            return []
        if self.prod_display_type == "prod_per_line":
            return [
                ", ".join(variant.product_template_attribute_value_ids.mapped("display_name"))
                for variant in product.product_variant_ids
            ]
        if self.prod_display_type == "prod_list" and len(product.product_variant_ids) > 1:
            return [
                " / ".join(
                    [
                        " ".join(variant.product_template_attribute_value_ids.mapped("name"))
                        for variant in product.product_variant_ids
                    ]
                )
            ]
        if self.prod_display_type == "variants":
            return [
                "%s: %s" % (line.attribute_id.name, ", ".join(line.value_ids.mapped("name")))
                for line in product.attribute_line_ids
            ]
        return []

    def get_price(self, product, pricelist):
        self.ensure_one()
        product_obj = self.env[self.product_type].with_context(pricelist=pricelist.id, whole_pack_price=True)
        sale_uom = self.env["product.template"].fields_get(["sale_uom_ids"])
        if sale_uom and product.sale_uom_ids:
            product_obj = product_obj.with_context(uom=product.sale_uom_ids[0].uom_id.id)
        price = product_obj.browse([product.id])._get_contextual_price()
        taxes_included = self.env.context.get("taxes_included", self.taxes_included)
        if taxes_included:
            taxes = product.taxes_id.filtered(lambda tax: tax.company_id == self.env.company)
            price = taxes.compute_all(
                price,
                currency=pricelist.currency_id,
                quantity=1.0,
                product=product,
            )["total_included"]
        return price

    def get_formatted_price(self, product, pricelist):
        self.ensure_one()
        price = self.get_price(product, pricelist)
        return formatLang(self.env, price, currency_obj=pricelist.currency_id)

    def get_description(self, product):
        self.ensure_one()
        sale_uom = self.env["product.template"].fields_get(["sale_uom_ids"])
        product = product.with_context(display_default_code=False)
        if not self.print_product_uom:
            return product.display_name
        if sale_uom and product.sale_uom_ids:
            main_uom = product.sale_uom_ids[0].uom_id
        else:
            main_uom = product.uom_id
        description = "%s (%s)" % (product.display_name, main_uom.display_name)
        if sale_uom and len(product.sale_uom_ids) > 1:
            description = _("%s. Also available in %s") % (
                description,
                ", ".join(product.sale_uom_ids.filtered(lambda x: x.uom_id != main_uom).mapped("uom_id.display_name")),
            )
        return description

    def generate_report(self):
        """Print the catalog (PDF via QWeb or XLSX via controller)."""
        self.ensure_one()
        self = self.prepare_report()
        xlsx_report = self.env.ref(
            "product_catalog_aeroo_report.report_product_catalog_ods",
            raise_if_not_found=False,
        )
        if xlsx_report and self.report_id == xlsx_report:
            from urllib.parse import urlencode

            params = urlencode(
                {
                    "taxes_included": int(bool(self.env.context.get("taxes_included", self.taxes_included))),
                    "use_planned_price": int(bool(self.env.context.get("use_planned_price"))),
                }
            )
            return {
                "type": "ir.actions.act_url",
                "url": "/product_catalog/%d/export.xlsx?%s" % (self.id, params),
                "target": "self",
            }
        return self.report_id.report_action(self)
