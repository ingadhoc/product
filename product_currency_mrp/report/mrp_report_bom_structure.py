from odoo import api, fields, models


class ReportReplenishmentBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_component_data(
        self,
        parent_bom,
        parent_product,
        warehouse,
        bom_line,
        line_quantity,
        level,
        index,
        product_info,
        ignore_stock=False,
    ):
        res = super()._get_component_data(
            parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock
        )
        currency = self.env.context.get("force_currency") or self.env.company.currency_id
        company = parent_bom.company_id or self.env.company
        price = (
            bom_line.product_id.uom_id._compute_price(
                bom_line.product_id.with_company(company).standard_price, bom_line.product_uom_id
            )
            * line_quantity
        )
        price_converted = currency._convert(
            price, self.env.company.currency_id, (parent_bom.company_id or self.env.company), fields.Date.today()
        )
        rounded_price = currency.round(price_converted)
        res.update(
            {
                "currency": currency,
                "currency_id": currency.id,
                "prod_cost": rounded_price,
            }
        )
        return res
