from odoo import api, fields, models
from odoo.tools import float_compare

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    is_alert_date = fields.Boolean(compute='_compute_is_alert_date', help="The Alert Date has been reached")

    @api.depends('alert_date')
    def _compute_is_alert_date(self):
        current_date = fields.Datetime.now()
        for lot in self:
            if lot.alert_date:
                lot.is_alert_date = (lot.alert_date <= current_date)
            else:
                lot.is_alert_date = False
