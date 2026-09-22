from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCurrencyDemo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["product.template"]._install_product_currency_demo()
        cls.demo_product_usd = cls.env.ref("product_currency.demo_product_usd")
        cls.demo_product_eur = cls.env.ref("product_currency.product_with_forced_currency")

    def test_demo_product_usd_exists(self):
        self.assertTrue(self.demo_product_usd.force_currency_id)
        self.assertEqual(self.demo_product_usd.force_currency_id, self.env.ref("base.USD"))

    def test_demo_product_eur_force_currency(self):
        self.assertEqual(self.demo_product_eur.force_currency_id, self.env.ref("base.EUR"))

    def test_idempotent(self):
        """Segunda llamada no duplica ni pisa registros (noupdate=True via _load_records)."""
        self.env["product.template"]._install_product_currency_demo()
        self.assertEqual(
            self.env["ir.model.data"].search_count(
                [("module", "=", "product_currency"), ("name", "=", "demo_product_usd")]
            ),
            1,
        )
