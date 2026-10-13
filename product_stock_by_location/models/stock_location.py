##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    show_stock_on_products = fields.Boolean(
        string="Show stock on products and sales",
        default=True,
        help="If set, this location's stock is shown on products: the stock detail on"
        " sale order lines and the pop up window opened from the products kanban and"
        " list view. Enabled by default; uncheck it on locations you do not want to"
        " expose (e.g. scrap/discard locations modelled as internal).",
    )
    qty_available = fields.Float(
        compute="_compute_product_available",
        digits="Product Unit of Measure",
        string="Quantity On Hand",
        help="Current quantity of products.\n"
        "In a context with a single Stock Location, this includes "
        "goods stored at this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods stored in the Stock Location of this Warehouse, or any "
        "of its children.\n"
        "stored in the Stock Location of the Warehouse of this Shop, "
        "or any of its children.\n"
        "Otherwise, this includes goods stored in any Stock Location "
        "with 'internal' type.",
    )
    virtual_available = fields.Float(
        compute="_compute_product_available",
        digits="Product Unit of Measure",
        string="Forecast Quantity",
        help="Forecast quantity (computed as Quantity On Hand "
        "- Outgoing + Incoming)\n"
        "In a context with a single Stock Location, this includes "
        "goods stored in this location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods stored in the Stock Location of this Warehouse, or any "
        "of its children.\n"
        "Otherwise, this includes goods stored in any Stock Location "
        "with 'internal' type.",
    )
    incoming_qty = fields.Float(
        compute="_compute_product_available",
        digits="Product Unit of Measure",
        string="Incoming",
        help="Quantity of products that are planned to arrive.\n"
        "In a context with a single Stock Location, this includes "
        "goods arriving to this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods arriving to the Stock Location of this Warehouse, or "
        "any of its children.\n"
        "Otherwise, this includes goods arriving to any Stock "
        "Location with 'internal' type.",
    )
    outgoing_qty = fields.Float(
        compute="_compute_product_available",
        digits="Product Unit of Measure",
        string="Outgoing",
        help="Quantity of products that are planned to leave.\n"
        "In a context with a single Stock Location, this includes "
        "goods leaving this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods leaving the Stock Location of this Warehouse, or "
        "any of its children.\n"
        "Otherwise, this includes goods leaving any Stock "
        "Location with 'internal' type.",
    )

    @api.depends_context("active_model", "active_id")
    def _compute_product_available(self):
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        products = self.env["product.product"]
        if active_id and active_model == "product.template":
            products = self.env["product.template"].browse(active_id).product_variant_ids
        elif active_id and active_model == "product.product":
            products = products.browse(active_id)
        for rec in self:
            located = products.with_context(location=rec.id)
            rec.qty_available = sum(located.mapped("qty_available"))
            rec.virtual_available = sum(located.mapped("virtual_available"))
            rec.incoming_qty = sum(located.mapped("incoming_qty"))
            rec.outgoing_qty = sum(located.mapped("outgoing_qty"))
