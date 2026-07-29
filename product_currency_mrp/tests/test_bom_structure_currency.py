from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBomStructureCurrency(TransactionCase):
    """Products costed in a currency other than the company one, through
    force_currency_id. The BoM structure report must express every line in the
    product currency, instead of mixing nominal values of both currencies.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company_currency = cls.company.currency_id
        cls.rate = 1000.0
        # A currency of its own so the test does not depend on which currency
        # the company happens to use. 1 TSC = 1000 company currency units.
        cls.currency = cls.env["res.currency"].create(
            {
                "name": "TSC",
                "symbol": "TSC",
                "rounding": 0.01,
            }
        )
        cls.env["res.currency.rate"].create(
            {
                "name": fields.Date.today(),
                "currency_id": cls.currency.id,
                "company_id": cls.company.id,
                "inverse_company_rate": cls.rate,
            }
        )

        cls.component = cls.env["product.product"].create(
            {
                "name": "Component costed in TSC",
                "is_storable": True,
                "standard_price": 10.0,
                "force_currency_id": cls.currency.id,
            }
        )
        cls.finished = cls.env["product.product"].create(
            {
                "name": "Finished costed in TSC",
                "is_storable": True,
                "standard_price": 0.0,
                "force_currency_id": cls.currency.id,
            }
        )

    def _bom_report(self, bom):
        return self.env["report.mrp.report_bom_structure"]._get_report_data(bom_id=bom.id, searchQty=1)

    def test_component_cost_uses_product_currency(self):
        """A component costed at 10 TSC must be reported as 10 in a TSC BoM.

        Without the currency overrides the report falls back to the company
        currency, so the 10 is silently taken as 10 company currency units.
        """
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [(0, 0, {"product_id": self.component.id, "product_qty": 1.0})],
            }
        )
        report = self._bom_report(bom)

        self.assertEqual(report["lines"]["currency_id"], self.currency.id, "The BoM report must be expressed in TSC")
        component_line = report["lines"]["components"][0]
        self.assertEqual(component_line["currency_id"], self.currency.id)
        self.assertAlmostEqual(component_line["bom_cost"], 10.0, 2)
        self.assertAlmostEqual(report["lines"]["bom_cost"], 10.0, 2)

    def test_bom_data_without_product(self):
        """_get_bom_data takes product as an optional argument, so the currency
        has to fall back to the template instead of blowing up on False.
        """
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [(0, 0, {"product_id": self.component.id, "product_qty": 1.0})],
            }
        )
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        res = self.env["report.mrp.report_bom_structure"]._get_bom_data(bom, warehouse)

        self.assertEqual(res["currency_id"], self.currency.id)

    def test_subcontracting_and_components_share_one_currency(self):
        """Ticket 122531: subcontracted BoM whose supplier price is in TSC.

        The native subcontracting line converts the supplier price to the
        company currency (5 TSC -> 5000) while the component keeps its nominal
        10. Adding them up gives 5010, an amount in no currency at all. Both
        must land in the product currency: 5 + 10 = 15 TSC.
        """
        subcontractor = self.env["res.partner"].create({"name": "Subcontractor"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": subcontractor.id,
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "price": 5.0,
                "currency_id": self.currency.id,
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "subcontract",
                "subcontractor_ids": [(6, 0, subcontractor.ids)],
                "bom_line_ids": [(0, 0, {"product_id": self.component.id, "product_qty": 1.0})],
            }
        )
        report = self._bom_report(bom)

        self.assertEqual(report["lines"]["currency_id"], self.currency.id)
        self.assertAlmostEqual(
            report["lines"]["subcontracting"]["bom_cost"],
            5.0,
            2,
            "The supplier price is already in TSC, it must not be converted to the company currency",
        )
        self.assertAlmostEqual(report["lines"]["components"][0]["bom_cost"], 10.0, 2)
        self.assertAlmostEqual(
            report["lines"]["bom_cost"],
            15.0,
            2,
            "Total must add up amounts expressed in the same currency",
        )
