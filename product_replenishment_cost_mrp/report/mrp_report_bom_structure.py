from odoo import api, fields, models


class ReportReplenishmentBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_subcontracting_line(self, bom, seller, level, bom_quantity):
        """Override to convert seller price to the proper currency"""
        res = super()._get_subcontracting_line(bom, seller, level, bom_quantity)
        currency = self.env.context.get("force_currency") or self.env.company.currency_id

        # Convert the seller price to the proper currency
        if bom.product_uom_id.factor == 0:
            raise ValueError(
                "El ratio de la unidad de medida del producto en el BOM es cero. "
                "Esto provocaría una división por cero. Verifique la configuración de la UoM."
            )
        ratio_uom_seller = seller.product_uom_id.factor / bom.product_uom_id.factor
        price = seller.currency_id._convert(seller.price, currency, self.env.company, fields.Date.today(), round=True)
        res.update(
            {
                "prod_cost": price / ratio_uom_seller * bom_quantity,
                "bom_cost": price / ratio_uom_seller * bom_quantity,
                "currency": currency,
                "currency_id": currency.id,
            }
        )

        return res

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
        """Here we use the replenishment cost for the uom unit"""
        if not self.env.context.get("force_currency"):
            self = self.with_context(force_currency=product.currency_id if product else bom.product_tmpl_id.currency_id)
        res = super(ReportReplenishmentBomStructure, self)._get_bom_data(
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
        currency = self.env.context.get("force_currency") or self.env.company.currency_id
        res.update({"currency": currency, "currency_id": currency.id})
        is_minimized = self.env.context.get("minimized", False)
        current_quantity = line_qty
        if bom_line:
            current_quantity = bom_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id) or 0

        # Only update prod_cost (costo del producto final), not bom_cost
        # bom_cost is automatically calculated as: components + operations + subcontracting
        if not is_minimized:
            if product:
                price = product.uom_id._compute_price(product.replenishment_cost, bom.product_uom_id) * current_quantity
                res["prod_cost"] = product.currency_id._convert(
                    price, currency, self.env.company, fields.Date.today(), round=True
                )
            else:
                # Use the product template instead of the variant
                price = (
                    bom.product_tmpl_id.uom_id._compute_price(
                        bom.product_tmpl_id.replenishment_cost, bom.product_uom_id
                    )
                    * current_quantity
                )
                res["prod_cost"] = bom.product_tmpl_id.currency_id._convert(
                    price, currency, self.env.company, fields.Date.today(), round=True
                )
        return res

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

        # Use replenishment_cost, if not defined use standard_price as fallback
        component_cost = bom_line.product_id.replenishment_cost
        if not component_cost:
            component_cost = bom_line.product_id.standard_price

        price = bom_line.product_id.uom_id._compute_price(component_cost, bom_line.product_uom_id) * line_quantity
        price = bom_line.product_id.currency_id._convert(
            price, currency, self.env.company, fields.Date.today(), round=True
        )
        res.update(
            {
                "bom_cost": price,
                "currency": currency,
                "currency_id": currency.id,
                "prod_cost": price,
            }
        )
        return res

    @api.model
    def _get_byproducts_lines(self, product, bom, bom_quantity, level, total, index):
        byproducts, byproduct_cost_portion = super()._get_byproducts_lines(
            product, bom, bom_quantity, level, total, index
        )
        currency = self.env.context.get("force_currency") or self.env.company.currency_id
        for byproduct in byproducts:
            byproduct_id = self.env["mrp.bom.byproduct"].browse(byproduct["id"])
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * byproduct_id.product_qty
            price = (
                byproduct_id.product_id.uom_id._compute_price(
                    byproduct_id.product_id.replenishment_cost, byproduct_id.product_uom_id
                )
                * line_quantity
            )
            price = byproduct_id.product_id.currency_id._convert(
                price, currency, self.env.company, fields.Date.today(), round=True
            )
            byproduct.update(
                {
                    "currency_id": currency.id,
                    "prod_cost": price,
                }
            )
        return byproducts, byproduct_cost_portion

    @api.model
    def _get_operation_line(self, product, bom, qty, level, index, bom_report_line, simulated_leaves_per_workcenter):
        operations = super()._get_operation_line(
            product, bom, qty, level, index, bom_report_line, simulated_leaves_per_workcenter
        )
        currency = self.env.context.get("force_currency") or self.env.company.currency_id
        for operation in operations:
            bom_cost = self.env.company.currency_id._convert(
                operation["bom_cost"], currency, self.env.company, fields.Date.today(), round=True
            )
            operation.update(
                {
                    "currency_id": currency.id,
                    "bom_cost": bom_cost,
                }
            )
        return operations
