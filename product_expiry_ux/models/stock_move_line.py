# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import datetime
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero

class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    @api.onchange('expiration_date')
    def onchange_expiration_date(self):
        if self.lot_id and self.product_id:
            lot = self.env['stock.lot'].search([
                ('name', '=', self.lot_id.name),
                ('product_id', '=', self.product_id.id),
            ])
            prod = lot.product_id.product_tmpl_id
            lot.write({
                'expiration_date': self.expiration_date,
            })
            lot.write({
                'removal_date': lot.expiration_date - datetime.timedelta(days=prod.removal_time),
                'use_date': lot.expiration_date - datetime.timedelta(days=prod.use_time),
            })
            if not lot.alert_date:
                lot.write({'alert_date': lot.expiration_date - datetime.timedelta(days=prod.alert_time)})
