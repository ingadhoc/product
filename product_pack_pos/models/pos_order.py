from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _


class pos_order(models.Model):
    _inherit = "pos.order"

    def create_picking(self, cr, uid, ids, context=None):
        '''this call will create pickings for normal products'''
        super(pos_order, self).create_picking(
            cr, uid, ids, context=context)
        ''' Below code will create another picking for packs'''
        picking_obj = self.pool['stock.picking']
        partner_obj = self.pool['res.partner']
        move_obj = self.pool['stock.move']

        for order in self.browse(cr, uid, ids, context=context):
            addr = order.partner_id and partner_obj.address_get(
                cr, uid, [order.partner_id.id],
                ['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            if picking_type:
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': addr.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                }, context=context)
                self.write(cr, uid, [order.id], {
                           'picking_id': picking_id}, context=context)
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise osv.except_osv(_('Error!'), _(
                        'Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, [
                                                         'property_stock_customer'], context=context)['property_stock_customer']

            for line in order.lines:
                if line.product_id.pack:
                    for pack_line in line.product_id.pack_line_ids:

                        move_list = []

                        move_list.append(move_obj.create(cr, uid, {
                            'name': pack_line.product_id.name,
                            'product_uom': pack_line.product_id.uom_id.id,
                            'product_uos': pack_line.product_id.uom_id.id,
                            'picking_id': picking_id,
                            'picking_type_id': picking_type.id,
                            'product_id': pack_line.product_id.id,
                            'product_uos_qty': abs(pack_line.quantity * line.qty),
                            'product_uom_qty': abs(pack_line.quantity * line.qty),
                            'state': 'draft',
                            'location_id': location_id if line.qty >= 0 else destination_id,
                            'location_dest_id': destination_id if line.qty >= 0 else location_id,
                        }, context=context))

                        if picking_id:
                            picking_obj.action_confirm(
                                cr, uid, [picking_id], context=context)
                            picking_obj.force_assign(
                                cr, uid, [picking_id], context=context)
                            picking_obj.action_done(
                                cr, uid, [picking_id], context=context)
                        elif move_list:
                            move_obj.action_confirm(
                                cr, uid, move_list, context=context)
                            move_obj.force_assign(
                                cr, uid, move_list, context=context)
                            move_obj.action_done(
                                cr, uid, move_list, context=context)
        return True
