##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase


class TestPlannedPriceCompany(TransactionCase):
    def setUp(self):
        super().setUp()
        self.main_company = self.env.ref("base.main_company")
        self.currency = self.main_company.currency_id
        self.aux_company = self.env["res.company"].create(
            {
                "name": "Aux Co (121458)",
                "currency_id": self.currency.id,
            }
        )
        self.supplier = self.env["res.partner"].create({"name": "Proveedor 121458"})
        self.product = self.env["product.template"].create(
            {
                "name": "Producto 121458",
                "type": "consu",
                "list_price_type": "by_margin",
                "sale_margin": 50.0,
                "sale_surcharge": 0.0,
                "replenishment_cost_type": "supplier_price",
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.product.id,
                "partner_id": self.supplier.id,
                "company_id": self.aux_company.id,
                "currency_id": self.currency.id,
                "price": 100.0,
            }
        )

    def test_planned_price_uses_operating_company_cost(self):
        product_aux = self.product.with_company(self.aux_company)

        self.assertEqual(
            product_aux.replenishment_cost,
            100.0,
            "Replenishment cost should resolve to 100 in the auxiliary company",
        )

        self.assertEqual(
            product_aux.computed_list_price,
            150.0,
            "Planned price should be computed with the operating company cost " "(150), not the main company one (0)",
        )
