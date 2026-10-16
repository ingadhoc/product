##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductPriceTaxesIncluded(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Taxes Included Test 21%",
                "amount": 21.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "company_id": cls.company.id,
            }
        )
        cls.template = cls.env["product.template"].create(
            {
                "name": "Taxes Included Drill",
                "list_price": 100.0,
                "taxes_id": [(6, 0, cls.tax.ids)],
            }
        )
        cls.product = cls.template.product_variant_id
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Taxes Included Pricelist", "currency_id": cls.company.currency_id.id}
        )

    # Taxed sale price

    def test_taxed_lst_price_adds_the_tax_to_the_sale_price(self):
        """The taxed sale price is the sale price with its sale taxes applied."""
        self.assertEqual(self.template.taxed_lst_price, 121.0)
        self.assertEqual(self.product.taxed_lst_price, 121.0)

    def test_taxed_lst_price_ignores_taxes_of_another_company(self):
        """Only the taxes of the company in the context are applied."""
        other_company = self.env["res.company"].create({"name": "Taxes Included Other Co"})
        other_group = self.env["account.tax.group"].create(
            {"name": "Taxes Included Other Group", "company_id": other_company.id}
        )
        other_tax = self.env["account.tax"].create(
            {
                "name": "Taxes Included Other 10%",
                "amount": 10.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "company_id": other_company.id,
                "tax_group_id": other_group.id,
                "country_id": self.tax.country_id.id,
            }
        )
        self.template.taxes_id = [(6, 0, (self.tax | other_tax).ids)]

        self.assertEqual(self.template.taxed_lst_price, 121.0)

    def test_taxed_lst_price_without_taxes_is_the_sale_price(self):
        """A product with no sale taxes keeps its sale price."""
        self.template.taxes_id = [(5, 0, 0)]

        self.assertEqual(self.template.taxed_lst_price, 100.0)

    # taxes_included on the pricelist

    def test_pricelist_price_without_context_has_no_taxes(self):
        """Without the context the pricelist price is the one of Odoo."""
        self.assertEqual(self.pricelist._get_product_price(self.product, 1.0), 100.0)
        self.assertEqual(self.pricelist._get_products_price(self.product, 1.0), {self.product.id: 100.0})

    def test_pricelist_price_with_context_includes_the_taxes(self):
        """With taxes_included on the context the pricelist price carries the taxes."""
        pricelist = self.pricelist.with_context(taxes_included=True)

        self.assertEqual(pricelist._get_product_price(self.product, 1.0), 121.0)
        self.assertEqual(pricelist._get_products_price(self.product, 1.0), {self.product.id: 121.0})

    def test_pricelist_price_with_context_applies_the_rule_before_the_taxes(self):
        """The taxes are computed on the price the pricelist rule returns."""
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
                "compute_price": "fixed",
                "fixed_price": 200.0,
            }
        )
        pricelist = self.pricelist.with_context(taxes_included=True)

        self.assertEqual(pricelist._get_product_price(self.product, 1.0), 242.0)

    def test_pricelist_price_adds_the_taxes_only_once(self):
        """_get_product_price goes through _get_products_price: the taxes are not applied twice."""
        pricelist = self.pricelist.with_context(taxes_included=True)

        self.assertEqual(
            pricelist._get_product_price(self.product, 1.0),
            pricelist._get_products_price(self.product, 1.0)[self.product.id],
        )
