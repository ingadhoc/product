from odoo import models, fields
from odoo.tools import float_round


class ReportReplenishmentBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        """ Here we use the replenishment cost for the uom unit"""
        res = super()._get_bom(bom_id=bom_id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
        bom = self.env['mrp.bom'].browse(bom_id)
        bom_quantity = line_qty
        if line_id:
            current_line = self.env['mrp.bom.line'].browse(int(line_id))
            bom_quantity = current_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id) or 0
        if res.get('product_id', False) and res['product_id']:
            product = self.env['product.product'].browse(res['product_id'])
            res['price'] = product.uom_id._compute_price(product.replenishment_cost, bom.product_uom_id) * bom_quantity
        return res

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components, total = super()._get_bom_lines(bom, bom_quantity, product, line_id, level)
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (
                bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            price = line.product_id.uom_id._compute_price(
                line.product_id.replenishment_cost, line.product_uom_id) * line_quantity
            price = line.product_id.currency_id._convert(
                price, product.currency_id, self.env.company, fields.Date.today(), round=True)
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(
                    line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(
                    line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = line.product_id.currency_id.round(sub_total)
            for comp in components:
                if comp['line_id'] == line.id:
                    comp['prod_cost'] = price
                    comp['total'] = sub_total
                    break
            total += sub_total
        return components, total

    def _get_price(self, bom, factor, product):
        price = 0
        if bom.routing_id:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(
                factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(
                bom.routing_id, operation_cycle, 0)
            price += sum([op['total'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(
                    line.product_qty * factor, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price(
                    line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor
                not_rounded_price = line.product_id.uom_id._compute_price(
                    line.product_id.replenishment_cost, line.product_uom_id) * prod_qty
                price += product.currency_id.round(
                    not_rounded_price)
        return price
