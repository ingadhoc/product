##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged
from odoo.tools.image import image_to_base64
from PIL import Image


@tagged("post_install", "-at_install")
class TestProductCatalogPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Catalog tax 21%",
                "amount_type": "percent",
                "amount": 21.0,
                "type_tax_use": "sale",
            }
        )
        cls.product, cls.other_product = cls.env["product.template"].create(
            [
                {"name": "Catalog product", "list_price": 100.0, "taxes_id": [(6, 0, cls.tax.ids)]},
                {"name": "Catalog product 2", "list_price": 250.0, "taxes_id": [(6, 0, cls.tax.ids)]},
            ]
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Catalog pricelist",
                "item_ids": [(0, 0, {"applied_on": "3_global", "compute_price": "formula", "base": "list_price"})],
            }
        )
        cls.catalog = cls.env["product.product_catalog_report"].create(
            {
                "name": "Catalog",
                "product_type": "product.template",
                "prod_display_type": "prod_per_line",
                "pricelist_ids": [(6, 0, cls.pricelist.ids)],
                "report_id": cls.env.ref("product_catalog_aeroo_report.report_product_catalog_simple_odt").id,
            }
        )

    def test_price_without_taxes(self):
        self.assertAlmostEqual(self.catalog.get_price(self.product, self.pricelist), 100.0)

    def test_taxes_are_added_once_from_context(self):
        """The pricelist already returns the price with taxes, so the catalog
        must not add them a second time."""
        price = self.catalog.with_context(taxes_included=True).get_price(self.product, self.pricelist)
        self.assertAlmostEqual(price, 121.0)

    def test_taxes_are_added_once_from_record(self):
        """Same result when the flag comes from the catalog instead of the context."""
        self.catalog.taxes_included = True
        self.assertAlmostEqual(self.catalog.get_price(self.product, self.pricelist), 121.0)

    def test_batch_prices_match_single_price(self):
        """The catalog asks the pricelist once for every product, so the batch
        must return what the per product call returns."""
        catalog = self.catalog.with_context(taxes_included=True)
        products = self.product | self.other_product
        prices = catalog.get_prices(products)
        self.assertEqual(sorted(prices), self.pricelist.ids)
        self.assertEqual(
            prices[self.pricelist.id],
            {product.id: catalog.get_price(product, self.pricelist) for product in products},
        )

    def test_batch_prices_are_formatted(self):
        catalog = self.catalog.with_context(taxes_included=True)
        formatted = catalog.get_formatted_prices(self.product)
        self.assertEqual(
            formatted[self.pricelist.id][self.product.id],
            catalog.get_formatted_price(self.product, self.pricelist),
        )

    def test_image_is_embedded_as_data_uri(self):
        """The catalog embeds the image instead of pointing at a url, so the
        pdf engine does not fetch one image per row."""
        self.product.image_1920 = image_to_base64(Image.new("RGB", (10, 10)), "PNG")
        self.assertTrue(self.catalog.get_image(self.product).startswith("data:image/"))

    def test_product_without_image(self):
        self.assertFalse(self.catalog.get_image(self.other_product))
