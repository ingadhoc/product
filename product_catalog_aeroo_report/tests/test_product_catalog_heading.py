##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from freezegun import freeze_time
from lxml import html as html_parser
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCatalogHeading(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create({"name": "Catalog category"})
        cls.products = cls.env["product.template"].create(
            [
                {"name": "Catalog product one", "list_price": 100.0, "categ_id": cls.category.id},
                {"name": "Catalog product two", "list_price": 200.0, "categ_id": cls.category.id},
            ]
        )
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Catalog pricelist"})
        cls.catalog = cls.env["product.product_catalog_report"].create(
            {
                "name": "Spring selection",
                "product_type": "product.template",
                "prod_display_type": "prod_per_line",
                "category_ids": [(6, 0, cls.category.ids)],
                "pricelist_ids": [(6, 0, cls.pricelist.ids)],
                "report_id": cls.env.ref("product_catalog_aeroo_report.report_product_catalog_simple_odt").id,
            }
        )

    def _render(self, catalog, report="report_product_catalog_qweb_simple"):
        html, _report_type = (
            self.env["ir.actions.report"]
            .with_env(catalog.env)
            ._render_qweb_html("product_catalog_aeroo_report.%s" % report, catalog.ids)
        )
        return html.decode() if isinstance(html, bytes) else html

    def _heading(self, html):
        """The div.header that the report engine hoists to the running page header."""
        tree = html_parser.fromstring(html)
        headings = tree.xpath(
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' header ')]"
            "[.//h2[normalize-space()='Price list']]"
        )
        self.assertTrue(headings, "the catalog heading is not inside a header div")
        return headings[0]

    @freeze_time("2026-01-25")
    def test_report_date_follows_the_user_language(self):
        """Day 25 is not a month, so d/m and m/d formats differ: the date
        follows the user language instead of a fixed pattern."""
        self.env["res.lang"]._activate_lang("es_ES")
        date_en = self.catalog.with_context(lang="en_US").get_report_date()
        date_es = self.catalog.with_context(lang="es_ES").get_report_date()
        self.assertIn("2026", date_en)
        self.assertNotEqual(date_en, date_es)

    def test_heading_prints_the_date(self):
        heading = self._heading(self._render(self.catalog))
        self.assertIn(self.catalog.get_report_date(), heading.text_content())

    def test_heading_shows_the_fixed_label_not_the_catalog_name(self):
        """18 printed the fixed "Price list" label, never the catalog name."""
        heading = self._heading(self._render(self.catalog))
        title = heading.xpath(".//h2")[0].text_content().strip()
        self.assertEqual(title, "Price list")
        self.assertNotIn(self.catalog.name, heading.text_content())

    def test_heading_lives_in_the_running_page_header(self):
        """The title hangs from a div.header, which is what makes the report
        engine repeat it on every page, as the odt master-page header did."""
        tree = html_parser.fromstring(self._render(self.catalog))
        title = tree.xpath("//h2[normalize-space()='Price list']")
        self.assertTrue(title, "heading title not found")
        ancestor_classes = " ".join(a.get("class") or "" for a in title[0].iterancestors())
        self.assertIn("header", ancestor_classes.split())

    def test_heading_states_taxes_are_not_included(self):
        """The Aeroo report always printed the legend, both ways."""
        text = self._heading(self._render(self.catalog)).text_content()
        self.assertIn("Prices do not include taxes", text)
        self.assertNotIn("Prices include taxes", text)

    def test_heading_states_taxes_are_included(self):
        text = self._heading(self._render(self.catalog.with_context(taxes_included=True))).text_content()
        self.assertIn("Prices include taxes", text)
        self.assertNotIn("Prices do not include taxes", text)

    def test_product_column_is_not_labelled_description(self):
        """18 labelled the column "Producto", not "Descripción"."""
        tree = html_parser.fromstring(self._render(self.catalog))
        headers = [th.text_content().strip() for th in tree.xpath("//thead//th")]
        self.assertIn("Product", headers)
        self.assertNotIn("Description", headers)

    def test_by_categories_report_lists_the_products(self):
        html = self._render(self.catalog, "report_product_catalog_qweb_by_categories")
        self.assertIn(self.category.name, html)
        for product in self.products:
            self.assertIn(product.name, html)
        self.assertIn(self.catalog.get_report_date(), self._heading(html).text_content())
