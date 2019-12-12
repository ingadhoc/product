from odoo import models
from odoo.tools import float_round


class ReportReplenishmentBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom(
            self, bom_id=False, product_id=False, line_qty=False, line_id=False,
            level=False):
        bom = self.env['mrp.bom'].browse(bom_id)
        bom_quantity = line_qty
        if line_id:
            current_line = self.env['mrp.bom.line'].browse(int(line_id))
            bom_quantity = current_line.product_uom_id._compute_quantity(
                line_qty, bom.product_uom_id)
        # Display bom components for current selected product variant
        if product_id:
            product = self.env['product.product'].browse(int(product_id))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        if product:
            attachments = self.env['mrp.document'].search(
                ['|', '&', ('res_model', '=', 'product.product'),
                 ('res_id', '=', product.id),
                 '&', ('res_model', '=', 'product.template'),
                 ('res_id', '=', product.product_tmpl_id.id)])
        else:
            product = bom.product_tmpl_id
            attachments = self.env['mrp.document'].search(
                [('res_model', '=', 'product.template'), ('res_id', '=', product.id)])
        operations = self._get_operation_line(bom.routing_id, float_round(
            bom_quantity / bom.product_qty, precision_rounding=1, rounding_method='UP'), 0)
        lines = {
            'bom': bom, 'bom_qty': bom_quantity,
            'bom_prod_name': product.display_name,
            'currency': self.env.user.company_id.currency_id,
            'product': product, 'code': bom and self._get_bom_reference(bom)
            or '', 'price': product.uom_id._compute_price(
                product.replenishment_cost, bom.product_uom_id) * bom_quantity,
            'total': sum([op['total'] for op in operations]),
            'level': level or 0, 'operations': operations,
            'operations_cost': sum([op['total'] for op in operations]),
            'attachments': attachments,
            'operations_time':
            sum([op['duration_expected'] for op in operations])}
        components, total = self._get_bom_lines(
            bom, bom_quantity, product, line_id, level)
        lines['components'] = components
        lines['total'] += total
        return lines

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (
                bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            price = line.product_id.uom_id._compute_price(
                line.product_id.replenishment_cost, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(
                    line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(
                    line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = self.env.user.company_id.currency_id.round(sub_total)
            components.append({
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and self._get_bom_reference(line.child_bom_id) or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': self.env.user.company_id.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                                                                ('res_model', '=', 'product.product'),
                                                                ('res_id', '=', line.product_id.id),
                                                                '&',
                                                                ('res_model', '=', 'product.template'),
                                                                ('res_id', '=', line.product_id.product_tmpl_id.id)]),

            })
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
                price += self.env.user.company_id.currency_id.round(
                    not_rounded_price)
        return price
