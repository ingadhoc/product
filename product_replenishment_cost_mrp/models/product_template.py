from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    replenishment_cost_type = fields.Selection(
        selection_add=[("bom", "Basado en Ldm")], ondelete={"bom": "set default"}
    )

    @api.onchange("replenishment_cost_type")
    def onchange_replenishment_cost_type(self):
        if self.replenishment_cost_type == "bom" and not self._origin.bom_ids:
            raise UserError(
                _(
                    'If you choose replenishment cost type "Based on BoM" '
                    "then the product must have a bill of materials."
                )
            )

    @api.depends(
        # TODO ver si encontramos otra alternativa a este depends ya que esto lo hace bastante malo a nivel performance
        # antes usabamos un invalidate cache pero nos dejó de funcionar
        "bom_ids.bom_line_ids.product_qty",
        "bom_ids.bom_line_ids.product_uom_id",
    )
    def _compute_replenishment_cost(self):
        bom_costs = self.filtered(lambda x: x.replenishment_cost_type == "bom")
        company = self.env.company
        date = fields.Date.today()
        res = super(ProductTemplate, self - bom_costs)._compute_replenishment_cost()
        for rec in bom_costs:
            product_currency = rec.currency_id

            # robamos metodo de calculo de costo de product_extended
            price = 0.0
            bom = (
                self.env["mrp.bom"]._bom_find(rec.product_variant_ids[:1])[rec.product_variant_ids[:1]]
                if self.env["mrp.bom"]._bom_find(rec.product_variant_ids[:1])[rec.product_variant_ids[:1]]
                else self.env["mrp.bom"]._bom_find(rec.with_context(active_test=False).product_variant_ids[:1])[
                    rec.with_context(active_test=False).product_variant_ids[:1]
                ]
            )
            if not bom:
                rec.update({"replenishment_base_cost_on_currency": 0.0, "replenishment_cost": 0.0})
                continue
            # el explode es para product.product, tomamos la primer variante
            result, result2 = bom.explode(rec.with_context(active_test=rec.active).product_variant_ids[0], 1)
            for sbom, sbom_data in result2:
                sbom_rep_cost = (
                    sbom.product_id.uom_id._compute_price(
                        sbom.product_id.product_tmpl_id.replenishment_cost, sbom.product_uom_id
                    )
                    * sbom_data["qty"]
                )
                price += sbom.product_id.product_tmpl_id.currency_id._convert(
                    sbom_rep_cost, product_currency, company, date, round=False
                )
            # NO implementamos total va a ser borrado. Ver si implementamos mas adelante (tener en cuenta convertir
            # moneda)
            # if bom.routing_id:
            #     # FIXME master: remove me
            #     if hasattr(self.env['mrp.workcenter'], 'costs_hour'):
            #         total_cost = 0.0
            #         for order in bom.routing_id.operation_ids:
            #             total_cost += (order.time_cycle/60) * order.workcenter_id.costs_hour
            #         price += bom.product_uom_id._compute_price(total_cost, bom.product_id.uom_id)
            # Convert on product UoM quantities
            if price > 0:
                price = bom.product_uom_id._compute_price(price / bom.product_qty, rec.uom_id)

            replenishment_base_cost_on_currency = replenishment_cost = price
            if rec.replenishment_cost_rule_id:
                replenishment_cost = rec.replenishment_cost_rule_id.compute_rule(
                    replenishment_base_cost_on_currency, rec
                )
            rec.update(
                {
                    "replenishment_base_cost_on_currency": replenishment_base_cost_on_currency,
                    "replenishment_cost": replenishment_cost,
                }
            )
        return res

    def _update_cost_from_replenishment_cost(self):
        """ Override para procesar productos BOM en el orden correcto.
        Si un producto BOM tiene componentes que también están en el batch,
        primero se actualizan los componentes (hojas) y luego los padres.
        Esto es necesario porque replenishment_cost (store=False) se computa
        al vuelo y necesita ver el standard_price ya actualizado de sus
        componentes.
        """
        bom_templates = self.filtered(lambda t: t.replenishment_cost_type == 'bom')
        non_bom_templates = self - bom_templates

        # Los non-bom no dependen de otros, se procesan juntos normalmente
        if non_bom_templates:
            super(ProductTemplate, non_bom_templates)._update_cost_from_replenishment_cost()

        if not bom_templates:
            return True

        # Obtener los componentes BOM de cada template (solo los que están en nuestro batch)
        bom_tmpl_ids = set(bom_templates.ids)
        bom_components = {}  # {template_id: set of component template_ids in batch}
        for tmpl in bom_templates:
            comp_ids = set()
            for line in tmpl.bom_ids[:1].bom_line_ids:
                comp_tmpl_id = line.product_id.product_tmpl_id.id
                if comp_tmpl_id in bom_tmpl_ids:
                    comp_ids.add(comp_tmpl_id)
            bom_components[tmpl.id] = comp_ids

        # Ordenar: primero los que no dependen de nadie del batch (componentes),
        # luego los que dependen de ellos
        processed = set()
        sorted_templates = self.browse()
        # Iterar hasta procesar todos (máx N iteraciones para evitar loop infinito en ciclos)
        for _i in range(len(bom_templates) + 1):
            if len(processed) == len(bom_tmpl_ids):
                break
            # En cada pasada, agregar los que ya tienen todas sus dependencias procesadas
            ready = [
                tid for tid in bom_tmpl_ids - processed
                if bom_components[tid] <= processed
            ]
            if not ready:
                # Dependencia circular: agregar los restantes y loguear warning
                ready = list(bom_tmpl_ids - processed)
            sorted_templates |= self.browse(ready)
            processed.update(ready)

        # Procesar de a uno invalidando cache entre cada uno para que
        # el siguiente vea el standard_price actualizado de sus componentes
        for tmpl in sorted_templates:
            super(ProductTemplate, tmpl)._update_cost_from_replenishment_cost()
            tmpl.invalidate_recordset(['replenishment_cost', 'replenishment_base_cost_on_currency'])

        return True
