from odoo.tests.common import TransactionCase


class TestPlannedPriceContext(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create(
            {
                "name": "Planned Price Context Product",
                "list_price": 100.0,
                "list_price_type": "manual",
                "computed_list_price_manual": 150.0,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Planned Price Test Pricelist", "currency_id": cls.env.company.currency_id.id}
        )

    def _pricelist_price(self, **context):
        # the catalog report runs with the context set, so both the pricelist and
        # the products carry it
        variant = self.product.product_variant_id.with_context(**context)
        pricelist = self.pricelist.with_context(**context)
        return pricelist._get_products_price(variant, 1.0)[variant.id]

    def test_pricelist_uses_list_price_by_default(self):
        self.assertAlmostEqual(self._pricelist_price(), 100.0, places=2)

    def test_pricelist_uses_planned_price_with_context(self):
        """This is what the catalog report sends when its checkbox is ticked."""
        self.assertAlmostEqual(self._pricelist_price(use_planned_price=True), 150.0, places=2)

    def test_price_compute_uses_planned_price_with_context(self):
        variant = self.product.product_variant_id
        self.assertAlmostEqual(
            variant.with_context(use_planned_price=True)._price_compute("list_price")[variant.id],
            150.0,
            places=2,
        )
        self.assertAlmostEqual(
            self.product.with_context(use_planned_price=True)._price_compute("list_price")[self.product.id],
            150.0,
            places=2,
        )

    def test_other_price_types_ignore_the_context(self):
        self.product.standard_price = 42.0
        variant = self.product.product_variant_id
        self.assertAlmostEqual(
            variant.with_context(use_planned_price=True)._price_compute("standard_price")[variant.id],
            42.0,
            places=2,
        )
