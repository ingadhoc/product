##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase


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
