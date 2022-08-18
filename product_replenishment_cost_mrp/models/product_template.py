from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    replenishment_cost_type = fields.Selection(
        selection_add=[('bom', 'Basado en Ldm')], ondelete={'bom': 'set default'}
    )

    @api.onchange('replenishment_cost_type')
    def onchange_replenishment_cost_type(self):
        if self.replenishment_cost_type == 'bom' and not self._origin.bom_ids:
            raise UserError(_(
                'If you choose replenishment cost type "Based on BoM" '
                'then the product must have a bill of materials.'))

    @api.depends(
        # TODO ver si encontramos otra alternativa a este depends ya que esto lo hace bastante malo a nivel performance
        # antes usabamos un invalidate cache pero nos dejó de funcionar
        'bom_ids.bom_line_ids.product_qty',
        'bom_ids.bom_line_ids.product_uom_id',
    )
    def _compute_replenishment_cost(self):
        bom_costs = self.filtered(lambda x: x.replenishment_cost_type == 'bom')
        company = self.env.company
        date = fields.Date.today()
        res = super(
            ProductTemplate, self - bom_costs)._compute_replenishment_cost()
        for rec in bom_costs:
            product_currency = rec.currency_id

            # robamos metodo de calculo de costo de product_extended
            price = 0.0
            bom = self.env['mrp.bom']._bom_find(rec.product_variant_ids[0])[rec.product_variant_ids[0]]
            if not bom:
                rec.update({
                    'replenishment_base_cost_on_currency': 0.0,
                    'replenishment_cost': 0.0
                })
                continue
            # el explode es para product.product, tomamos la primer variante
            result, result2 = bom.explode(rec.with_context(active_test=rec.active).product_variant_ids[0], 1)
            for sbom, sbom_data in result2:
                sbom_rep_cost = sbom.product_id.uom_id._compute_price(
                    sbom.product_id.product_tmpl_id.replenishment_cost,
                    sbom.product_uom_id) * sbom_data['qty']
                price += sbom.product_id.product_tmpl_id.currency_id._convert(
                    sbom_rep_cost, product_currency, company, date, round=False)
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
                price = bom.product_uom_id._compute_price(
                    price / bom.product_qty, rec.uom_id)

            replenishment_base_cost_on_currency = replenishment_cost = price
            if rec.replenishment_cost_rule_id:
                replenishment_cost =\
                    rec.replenishment_cost_rule_id.compute_rule(
                        replenishment_base_cost_on_currency, rec)
            rec.update({
                'replenishment_base_cost_on_currency':
                replenishment_base_cost_on_currency,
                'replenishment_cost': replenishment_cost
            })
        return res
