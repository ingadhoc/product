from odoo import fields
from odoo.tests.common import TransactionCase


class TestProductPlannedPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_currency = cls.env.company.currency_id
        cls.other_currency = cls.env["res.currency"].create({"name": "PPT", "symbol": "**PPT**"})
        # 2 units of PPT per unit of the company currency: 100 PPT convert to 50
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.other_currency.id,
                "company_rate": 2.0,
                "name": fields.Date.today(),
                "company_id": cls.env.company.id,
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Planned Price Test Product",
                "list_price": 1.0,
                "replenishment_cost_type": "manual",
                "replenishment_base_cost": 100.0,
                "replenishment_base_cost_currency_id": cls.company_currency.id,
            }
        )

    def test_replenishment_cost_is_the_margin_base(self):
        self.assertAlmostEqual(self.product.replenishment_cost_main_company, 100.0, places=2)

    def test_computed_price_manual(self):
        self.product.write({"list_price_type": "manual", "computed_list_price_manual": 150.0})
        self.assertAlmostEqual(self.product.computed_list_price, 150.0, places=2)

    def test_computed_price_by_margin(self):
        self.product.write({"list_price_type": "by_margin", "sale_margin": 20.0, "sale_surcharge": 5.0})
        # 100 * (1 + 20%) + 5
        self.assertAlmostEqual(self.product.computed_list_price, 125.0, places=2)

    def test_computed_price_other_currency(self):
        self.product.write(
            {
                "list_price_type": "other_currency",
                "other_currency_id": self.other_currency.id,
                "other_currency_list_price": 100.0,
            }
        )
        self.assertAlmostEqual(self.product.computed_list_price, 50.0, places=2)

    def test_computed_price_adds_included_taxes(self):
        tax = self.env["account.tax"].create(
            {
                "name": "Planned Price Included Tax",
                "amount_type": "percent",
                "amount": 10.0,
                "type_tax_use": "sale",
                "price_include_override": "tax_included",
            }
        )
        self.product.write(
            {
                "list_price_type": "manual",
                "computed_list_price_manual": 100.0,
                "taxes_id": [(6, 0, tax.ids)],
            }
        )
        self.assertAlmostEqual(self.product.computed_list_price, 110.0, places=2)

    def test_no_planned_type_computes_zero(self):
        self.product.write({"list_price_type": False, "computed_list_price_manual": 150.0})
        self.assertAlmostEqual(self.product.computed_list_price, 0.0, places=2)

    def test_update_prices_from_planned_writes_list_price(self):
        self.product.write({"list_price_type": "manual", "computed_list_price_manual": 150.0})
        self.product._update_prices_from_planned()
        self.product.invalidate_recordset(["list_price"])
        self.assertAlmostEqual(self.product.list_price, 150.0, places=2)

    def test_update_prices_from_planned_skips_products_without_type(self):
        self.product.write({"list_price_type": False, "list_price": 1.0})
        self.product._update_prices_from_planned()
        self.product.invalidate_recordset(["list_price"])
        self.assertAlmostEqual(self.product.list_price, 1.0, places=2)

    def test_use_planned_price_context_has_no_effect(self):
        """The override is named price_compute, a name core dropped before 18, so
        nothing calls it and the context toggle does not reach the price."""
        self.product.write({"list_price_type": "manual", "computed_list_price_manual": 150.0, "list_price": 100.0})
        variant = self.product.product_variant_id
        self.assertAlmostEqual(
            variant.with_context(use_planned_price=True)._price_compute("list_price")[variant.id],
            100.0,
            places=2,
        )

    def test_price_compute_returns_list_price(self):
        self.product.write({"list_price_type": "manual", "computed_list_price_manual": 150.0, "list_price": 100.0})
        variant = self.product.product_variant_id
        self.assertAlmostEqual(variant._price_compute("list_price")[variant.id], 100.0, places=2)
