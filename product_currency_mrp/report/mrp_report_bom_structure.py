from odoo import api, fields, models


class ReportReplenishmentBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
<<<<<<< HEAD
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
||||||| parent of 2ab32991 (temp)
    def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, index=0, product_info=False, ignore_stock=False):
        """ Here we use the product forced currency uom unit"""
        if not self.env.context.get('force_currency'):
            self = self.with_context(force_currency=product.currency_id)
        res = super(ReportReplenishmentBomStructure, self)._get_bom_data(bom, warehouse, product, line_qty, bom_line, level, parent_bom, index, product_info, ignore_stock)
        currency = self.env.context.get('force_currency') or self.env.company.currency_id
        res.update({
            'currency': currency,
            'currency_id': currency.id
        })
        is_minimized = self.env.context.get('minimized', False)
        current_quantity = line_qty
        if bom_line:
            current_quantity = bom_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id) or 0
        if not is_minimized:
            if product:
                price = product.uom_id._compute_price(product.standard_price, bom.product_uom_id) * current_quantity
                res['prod_cost'] = product.currency_id._convert(
                    price, currency, self.env.company, fields.Date.today(), round=True)
            else:
                price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.standard_price, bom.product_uom_id) * current_quantity
                res['prod_cost'] = bom.product_tmpl_id.currency_id._convert(
                    price, currency, self.env.company, fields.Date.today(), round=True)
        return res

    @api.model
    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock=False):
        res = super()._get_component_data(parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock)
        currency = self.env.context.get('force_currency') or self.env.company.currency_id
=======
    def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, parent_product=False, index=0, product_info=False, ignore_stock=False):
        """ Here we use the product forced currency uom unit"""
        if not self.env.context.get('force_currency'):
            self = self.with_context(force_currency=product.currency_id)
        res = super(ReportReplenishmentBomStructure, self)._get_bom_data(bom, warehouse, product, line_qty, bom_line, level, parent_bom, parent_product, index, product_info, ignore_stock)
        currency = self.env.context.get('force_currency') or self.env.company.currency_id
        res.update({
            'currency': currency,
            'currency_id': currency.id
        })
        is_minimized = self.env.context.get('minimized', False)
        current_quantity = line_qty
        if bom_line:
            current_quantity = bom_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id) or 0
        if not is_minimized:
            if product:
                price = product.uom_id._compute_price(product.standard_price, bom.product_uom_id) * current_quantity
                res['prod_cost'] = product.currency_id._convert(
                    price, currency, self.env.company, fields.Date.today(), round=True)
            else:
                price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.standard_price, bom.product_uom_id) * current_quantity
                res['prod_cost'] = bom.product_tmpl_id.currency_id._convert(
                    price, currency, self.env.company, fields.Date.today(), round=True)
        return res

    @api.model
    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock=False):
        res = super()._get_component_data(parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock)
        currency = self.env.context.get('force_currency') or self.env.company.currency_id
>>>>>>> 2ab32991 (temp)
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
