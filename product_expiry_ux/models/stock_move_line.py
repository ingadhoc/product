# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import datetime

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("expiration_date")
    def onchange_expiration_date(self):
        if self.lot_id and self.product_id:
            lot = self.env["stock.lot"].search(
                [
                    ("name", "=", self.lot_id.name),
                    ("product_id", "=", self.product_id.id),
                ]
            )
            prod = lot.product_id.product_tmpl_id
            lot.write(
                {
                    "expiration_date": self.expiration_date,
                }
            )
            dates_to_update = {}
            if prod.removal_time:
                dates_to_update["removal_date"] = lot.expiration_date - datetime.timedelta(days=prod.removal_time)
            if prod.use_time:
                dates_to_update["use_date"] = lot.expiration_date - datetime.timedelta(days=prod.use_time)

            if dates_to_update:
                lot.write(dates_to_update)
            if not lot.alert_date and prod.alert_time:
                lot.write({"alert_date": lot.expiration_date - datetime.timedelta(days=prod.alert_time)})
