##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields
from odoo.tests import TransactionCase, tagged
from odoo.tools import format_date


@tagged("post_install", "-at_install")
class TestProductCatalogHeading(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create({"name": "Catalog product", "list_price": 100.0})
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Catalog pricelist"})
        cls.catalog = cls.env["product.product_catalog_report"].create(
            {
                "name": "Catalog",
                "product_type": "product.template",
                "prod_display_type": "prod_per_line",
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

    def test_report_date_follows_the_user_language(self):
        self.assertEqual(
            self.catalog.get_report_date(),
            format_date(self.env, fields.Date.context_today(self.catalog)),
        )

    def test_heading_prints_the_date(self):
        self.assertIn(self.catalog.get_report_date(), self._render(self.catalog))

    def test_heading_states_taxes_are_not_included(self):
        """The Aeroo report always printed the legend, both ways."""
        html = self._render(self.catalog)
        self.assertIn("Prices do not include taxes", html)
        self.assertNotIn(">Prices include taxes<", html)

    def test_heading_states_taxes_are_included(self):
        html = self._render(self.catalog.with_context(taxes_included=True))
        self.assertIn("Prices include taxes", html)
        self.assertNotIn("Prices do not include taxes", html)

    def test_by_categories_report_shares_the_heading(self):
        html = self._render(self.catalog, "report_product_catalog_qweb_by_categories")
        self.assertIn(self.catalog.get_report_date(), html)
        self.assertIn("Prices do not include taxes", html)
