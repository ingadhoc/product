##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase, tagged


class TestReplenishmentCostBom(TransactionCase):
    """Costo de reposicion calculado desde la lista de materiales."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id

        cls.raw_1 = cls._create_manual_cost_template("RAW-1", 10.0)
        cls.raw_2 = cls._create_manual_cost_template("RAW-2", 10.0)

        # un nivel: terminado directo sobre insumos comprados
        cls.single_level = cls.env["product.template"].create({"name": "SINGLE LEVEL", "default_code": "SINGLE"})
        cls._create_bom(cls.single_level, [(cls.raw_1, 1), (cls.raw_2, 1)])

        # dos niveles: terminado sobre un sub armado que a su vez sale de su propia LdM
        cls.sub_assembly = cls.env["product.template"].create({"name": "SUB", "default_code": "SUB"})
        cls.finished = cls.env["product.template"].create({"name": "FINISHED", "default_code": "FINISHED"})
        cls._create_bom(cls.sub_assembly, [(cls.raw_1, 1), (cls.raw_2, 1)])
        cls._create_bom(cls.finished, [(cls.sub_assembly, 1), (cls.raw_1, 1)])

        (cls.single_level + cls.sub_assembly + cls.finished).replenishment_cost_type = "bom"

    @classmethod
    def _create_manual_cost_template(cls, default_code, cost):
        return cls.env["product.template"].create(
            {
                "name": default_code,
                "default_code": default_code,
                "replenishment_cost_type": "manual",
                "replenishment_base_cost": cost,
                "replenishment_base_cost_currency_id": cls.currency.id,
            }
        )

    @classmethod
    def _create_bom(cls, template, lines):
        return cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": template.id,
                "product_qty": 1,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": component.product_variant_id.id, "product_qty": qty})
                    for component, qty in lines
                ],
            }
        )

    def test_single_level_bom(self):
        self.env.invalidate_all()
        self.assertEqual(self.single_level.replenishment_cost, 20.0)

    def test_multi_level_bom(self):
        self.env.invalidate_all()
        self.assertEqual(self.sub_assembly.replenishment_cost, 20.0)
        self.env.invalidate_all()
        self.assertEqual(self.finished.replenishment_cost, 30.0)

    def test_multi_level_bom_computed_as_batch(self):
        """El sub armado y el terminado en el mismo lote no deben perder el costo del sub armado.

        Hay que iterar el recordset: browse() resetea el prefetch set y computa de a uno, que es
        justamente el escenario que no falla.
        """
        self.env.invalidate_all()
        templates = self.finished + self.sub_assembly + self.raw_1 + self.raw_2
        costs = {template.default_code: template.replenishment_cost for template in templates}
        self.assertEqual(costs["SUB"], 20.0)
        self.assertEqual(costs["FINISHED"], 30.0)

    def test_update_cost_computed_as_batch(self):
        """La accion sobre una seleccion que incluye toda la cadena debe grabar el costo completo."""
        self.env.invalidate_all()
        templates = self.finished + self.sub_assembly + self.raw_1 + self.raw_2
        templates._update_cost_from_replenishment_cost()
        self.assertEqual(self.sub_assembly.product_variant_id.standard_price, 20.0)
        self.assertEqual(self.finished.product_variant_id.standard_price, 30.0)

    def test_product_without_bom(self):
        no_bom = self.env["product.template"].create({"name": "NO BOM", "default_code": "NO-BOM"})
        no_bom.replenishment_cost_type = "bom"
        self.env.invalidate_all()
        self.assertEqual(no_bom.replenishment_cost, 0.0)


@tagged("post_install", "-at_install")
class TestBomReportStandardPriceFallback(TransactionCase):
    """Without a replenishment cost the report converts standard_price from the cost currency.

    post_install so product_currency_mrp's override of the report loads too; skips without
    product_currency, which is what forces a product currency other than the cost one.
    """

    def test_standard_price_fallback_converts_from_cost_currency(self):
        if "force_currency_id" not in self.env["product.template"]._fields:
            self.skipTest("product_currency is not installed")
        rate = 10.0  # 1 TSC = 10 company currency units
        foreign = self.env["res.currency"].create({"name": "TSC", "symbol": "TSC", "rounding": 0.01})
        self.env["res.currency.rate"].create(
            {
                "name": "2000-01-01",
                "currency_id": foreign.id,
                "company_id": self.env.company.id,
                "inverse_company_rate": rate,
            }
        )
        # No replenishment cost: both fall back to standard_price (company currency).
        component = self.env["product.product"].create(
            {"name": "COMP", "is_storable": True, "standard_price": 100.0, "force_currency_id": foreign.id}
        )
        finished = self.env["product.product"].create(
            {"name": "FIN", "is_storable": True, "standard_price": 50.0, "force_currency_id": foreign.id}
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": finished.product_tmpl_id.id,
                "bom_line_ids": [(0, 0, {"product_id": component.id, "product_qty": 3})],
            }
        )

        data = self.env["report.mrp.report_bom_structure"]._get_report_data(bom.id)
        # component via _get_component_data: 3 x 100 company = 30 TSC (not 300)
        self.assertEqual(data["lines"]["components"][0]["bom_cost"], 30.0)
        # finished product via _get_bom_data prod_cost: 50 company = 5 TSC
        self.assertEqual(data["lines"]["prod_cost"], 5.0)
