from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCurrencyDemo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ejecutar el hook de demo data explícitamente
        cls.env["product.template"]._install_product_currency_demo([cls.env.company])
        cls.demo_product = cls.env.ref("product_currency.demo_product_usd", raise_if_not_found=False)

    def test_demo_product_exists(self):
        """El producto demo debe existir y tener force_currency_id seteado."""
        self.assertTrue(self.demo_product, "No se encontró el producto demo")
        self.assertTrue(self.demo_product.force_currency_id, "El producto demo debe tener force_currency_id")

    def test_force_currency_applies(self):
        """currency_id debe ser igual a force_currency_id en el demo."""
        self.assertEqual(
            self.demo_product.force_currency_id.id,
            self.demo_product.currency_id.id,
            "currency_id debe ser igual a force_currency_id en el demo",
        )
        # Copiamos el producto y forzamos el campo force_currency_id
