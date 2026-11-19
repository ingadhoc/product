from odoo import api, fields, models


class ReportBomStructureExtraCost(models.AbstractModel):
    """mrp_account adds the BoM extra cost in the company currency; express it in the forced one."""

    _inherit = "report.mrp.report_bom_structure"

    def _extra_cost_delta(self, bom, amount):
        """Difference between amount in the forced currency and in the company currency."""
        currency = self.env.context.get("force_currency") or self.env.company.currency_id
        company = bom.company_id or self.env.company
        return company.currency_id._convert(amount, currency, company, fields.Date.today()) - amount

    @api.model
    def _get_bom_data(
        self,
        bom,
        warehouse,
        product=False,
        line_qty=False,
        bom_line=False,
        level=0,
        parent_bom=False,
        parent_product=False,
        index=0,
        product_info=False,
        ignore_stock=False,
        simulated_leaves_per_workcenter=False,
    ):
        if not self.env.context.get("force_currency"):
            self = self.with_context(force_currency=product.currency_id if product else bom.product_tmpl_id.currency_id)
        res = super()._get_bom_data(
            bom,
            warehouse,
            product,
            line_qty,
            bom_line,
            level,
            parent_bom,
            parent_product,
            index,
            product_info,
            ignore_stock,
            simulated_leaves_per_workcenter,
        )
        if bom.type == "normal" and bom.extra_cost:
            delta = self._extra_cost_delta(bom, bom.extra_cost * res["quantity"] * res.get("cost_share", 1))
            res["bom_cost"] += delta
            res["bom_unit_cost"] += bom.uom_id._compute_price(delta, res["product"].uom_id)
            res["bom_extra_cost"] = bom.extra_cost + self._extra_cost_delta(bom, bom.extra_cost)
        return res

    @api.model
    def _get_byproducts_lines(self, product, bom, bom_quantity, level, total, index):
        if bom.type == "normal" and bom.extra_cost:
            total += self._extra_cost_delta(bom, bom.extra_cost * bom_quantity)
        return super()._get_byproducts_lines(product, bom, bom_quantity, level, total, index)
