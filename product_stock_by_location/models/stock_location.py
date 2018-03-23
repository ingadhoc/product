##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class StockLocation(models.Model):

    _inherit = 'stock.location'

    show_stock_on_products = fields.Boolean(
        help='If true, this location will be shown on the pop up window opened'
        'from products kanban and tree view'
    )
    qty_available = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Quantity On Hand',
        help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type."
    )
    virtual_available = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Forecast Quantity',
        help="Forecast quantity (computed as Quantity On Hand "
             "- Outgoing + Incoming)\n"
             "In a context with a single Stock Location, this includes "
             "goods stored in this location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type."
    )
    incoming_qty = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Incoming',
        help="Quantity of products that are planned to arrive.\n"
             "In a context with a single Stock Location, this includes "
             "goods arriving to this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods arriving to the Stock Location of this Warehouse, or "
             "any of its children.\n"
             "Otherwise, this includes goods arriving to any Stock "
             "Location with 'internal' type."
    )
    outgoing_qty = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Outgoing',
        help="Quantity of products that are planned to leave.\n"
             "In a context with a single Stock Location, this includes "
             "goods leaving this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods leaving the Stock Location of this Warehouse, or "
             "any of its children.\n"
             "Otherwise, this includes goods leaving any Stock "
             "Location with 'internal' type."
    )

    @api.multi
    def _compute_product_available(self):
        template_id = self._context.get('template_id', False)
        product_id = self._context.get('product_id', False)
        if template_id:
            product = self.env['product.template'].browse(template_id)
        elif product_id:
            product = self.env['product.product'].browse(product_id)
        else:
            # it not template_id or product_id on context, return True
            return True
        for rec in self:
            product = product.with_context(location=rec.id)
            rec.qty_available = product.qty_available
            rec.virtual_available = product.virtual_available
            rec.incoming_qty = product.incoming_qty
            rec.outgoing_qty = product.outgoing_qty
