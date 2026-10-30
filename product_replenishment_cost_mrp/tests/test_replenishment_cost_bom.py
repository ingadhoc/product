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

    def test_bom_line_in_another_uom(self):
        """Una linea de la LdM en docenas convierte el costo de reposicion del componente, en el costo
        del producto y en el reporte de estructura."""
        dozen = self.env.ref("uom.product_uom_dozen")
        template = self.env["product.template"].create({"name": "DOZEN", "default_code": "DOZEN"})
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": template.id,
                "product_qty": 1,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": self.raw_1.product_variant_id.id, "product_qty": 1, "uom_id": dozen.id})
                ],
            }
        )
        template.replenishment_cost_type = "bom"
        self.env.invalidate_all()
        self.assertEqual(template.replenishment_cost, 120.0)

        lines = self.env["report.mrp.report_bom_structure"]._get_report_data(bom.id, searchQty=1)["lines"]
        self.assertEqual([component["bom_cost"] for component in lines["components"]], [120.0])
        self.assertEqual(lines["bom_cost"], 120.0)
        self.assertEqual(lines["currency"], template.currency_id)

    def test_bom_extra_cost(self):
        """El costo adicional de la LdM se suma por unidad fabricada, igual que en el reporte de estructura."""
        if "extra_cost" not in self.env["mrp.bom"]._fields:
            self.skipTest("mrp_account is not installed")
        template = self.env["product.template"].create({"name": "EXTRA", "default_code": "EXTRA"})
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": template.id,
                "product_qty": 2,
                "type": "normal",
                "extra_cost": 5.0,
                "bom_line_ids": [(0, 0, {"product_id": self.raw_1.product_variant_id.id, "product_qty": 1})],
            }
        )
        template.replenishment_cost_type = "bom"
        self.env.invalidate_all()
        # 10 / 2 of the component plus 5 of extra cost per unit
        self.assertEqual(template.replenishment_cost, 10.0)

        lines = self.env["report.mrp.report_bom_structure"]._get_report_data(bom.id, searchQty=1)["lines"]
        self.assertEqual(lines["bom_cost"], 10.0)

        # without invalidating: the change has to reach the product through the depends
        bom.extra_cost = 7.0
        self.assertEqual(template.replenishment_cost, 12.0)

    def test_subcontracted_bom(self):
        """En una LdM subcontratada se suma el precio del subcontratista, convertido a la unidad de la LdM."""
        if "subcontractor_ids" not in self.env["mrp.bom"]._fields:
            self.skipTest("mrp_subcontracting is not installed")
        subcontractor = self.env["res.partner"].create({"name": "Subcontractor"})
        template = self.env["product.template"].create(
            {
                "name": "SUBCONTRACTED",
                "default_code": "SUBCONTRACTED",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": subcontractor.id,
                            "price": 60.0,
                            # since 20.0 min_qty defaults to 1, which in dozens filters out a 1 unit purchase
                            "min_qty": 0.0,
                            "currency_id": self.currency.id,
                            "uom_id": self.env.ref("uom.product_uom_dozen").id,
                        },
                    )
                ],
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": template.id,
                "product_qty": 1,
                "type": "subcontract",
                "subcontractor_ids": [(6, 0, subcontractor.ids)],
                "bom_line_ids": [(0, 0, {"product_id": self.raw_1.product_variant_id.id, "product_qty": 2})],
            }
        )
        template.replenishment_cost_type = "bom"
        self.env.invalidate_all()
        self.assertEqual(template.replenishment_cost, 25.0)

        lines = self.env["report.mrp.report_bom_structure"]._get_report_data(bom.id, searchQty=1)["lines"]
        self.assertEqual(lines["subcontracting"]["bom_cost"], 5.0)
        self.assertEqual(lines["bom_cost"], 25.0)

    def test_bom_overview_button_help(self):
        """La ayuda queda en el boton del resumen de la LdM y no en otro boton de la caja."""
        action = self.env.ref("mrp.action_report_mrp_bom")
        arch = self.env.ref("mrp.mrp_bom_form_view")._get_combined_arch()
        helps = {button.get("name"): button.get("help") for button in arch.xpath("//div[@name='button_box']/button")}
        self.assertEqual(helps.pop(str(action.id)), "Estructura y costo según costo de reposición")
        self.assertFalse(any(helps.values()))
