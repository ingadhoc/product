##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTaxedLstPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.branch = cls.env["res.company"].create({"name": "Taxed price branch", "parent_id": cls.env.company.id})
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Taxed price 21%",
                "amount_type": "percent",
                "amount": 21.0,
                "type_tax_use": "sale",
            }
        )
        cls.product = cls.env["product.template"].create(
            {"name": "Taxed price product", "list_price": 100.0, "taxes_id": [(6, 0, cls.tax.ids)]}
        )

    def test_taxed_lst_price_on_the_company_that_owns_the_tax(self):
        self.assertAlmostEqual(self.product.with_company(self.env.company).taxed_lst_price, 121.0)

    def test_taxed_lst_price_on_a_branch(self):
        # taxes are set up on the parent company, the branch has to walk up to find them
        self.assertAlmostEqual(self.product.with_company(self.branch).taxed_lst_price, 121.0)

    def test_variant_taxed_lst_price_on_a_branch(self):
        variant = self.product.product_variant_id
        self.assertAlmostEqual(variant.with_company(self.branch).taxed_lst_price, 121.0)

    def test_pricelist_price_with_taxes_on_a_branch(self):
        pricelist = self.env["product.pricelist"].create({"name": "Taxed price pricelist"})
        price = (
            pricelist.with_company(self.branch)
            .with_context(taxes_included=True)
            ._get_product_price(self.product.product_variant_id, 1.0)
        )
        self.assertAlmostEqual(price, 121.0)

    def test_taxed_lst_price_on_a_branch_with_its_own_tax(self):
        # a branch with its own tax uses it instead of walking up to the parent one
        own_tax = self.env["account.tax"].create(
            {
                "name": "Taxed price 10.5%",
                "amount_type": "percent",
                "amount": 10.5,
                "type_tax_use": "sale",
                "company_id": self.branch.id,
                # the branch may have no fiscal country of its own, and the tax group is computed from it
                "country_id": self.tax.country_id.id,
            }
        )
        self.product.taxes_id = [(6, 0, (self.tax | own_tax).ids)]
        self.assertAlmostEqual(self.product.with_company(self.branch).taxed_lst_price, 110.5)
        self.assertAlmostEqual(self.product.with_company(self.env.company).taxed_lst_price, 121.0)
