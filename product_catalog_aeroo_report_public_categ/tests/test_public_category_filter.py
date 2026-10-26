##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPublicCategoryFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent_category = cls.env["product.public.category"].create({"name": "Catalog parent"})
        cls.child_category = cls.env["product.public.category"].create(
            {"name": "Catalog child", "parent_id": cls.parent_category.id}
        )
        cls.other_category = cls.env["product.public.category"].create({"name": "Catalog other"})
        cls.product = cls.env["product.template"].create(
            {"name": "In the parent category", "public_categ_ids": [(6, 0, cls.parent_category.ids)]}
        )
        cls.child_product = cls.env["product.template"].create(
            {"name": "In the child category", "public_categ_ids": [(6, 0, cls.child_category.ids)]}
        )
        cls.env["product.template"].create(
            {"name": "In another category", "public_categ_ids": [(6, 0, cls.other_category.ids)]}
        )

    def _catalog(self, categories, include_sub_categories=False):
        return self.env["product.product_catalog_report"].create(
            {
                "name": "Public category catalog",
                "product_type": "product.template",
                "prod_display_type": "prod_per_line",
                "category_type": "public_category",
                "report_id": self.env.ref("product_catalog_aeroo_report.report_product_catalog_simple_odt").id,
                "public_category_ids": [(6, 0, categories.ids)],
                "include_sub_categories": include_sub_categories,
            }
        )

    def test_catalog_of_a_public_category_has_its_products(self):
        """The products of the chosen public category reach the report."""
        catalog = self._catalog(self.parent_category)
        self.assertEqual(catalog.get_categories(), self.parent_category)
        self.assertIn(self.product, catalog.get_all_products())

    def test_catalog_of_a_public_category_leaves_out_the_others(self):
        catalog = self._catalog(self.parent_category)
        self.assertNotIn(self.child_product, catalog.get_all_products())

    def test_sub_categories_are_included_when_asked(self):
        catalog = self._catalog(self.parent_category, include_sub_categories=True)
        self.assertEqual(catalog.get_categories(), self.parent_category | self.child_category)
        products = catalog.get_all_products()
        self.assertIn(self.product, products)
        self.assertIn(self.child_product, products)
