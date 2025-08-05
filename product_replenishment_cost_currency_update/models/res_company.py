from odoo import api, models
from odoo.fields import Datetime
from datetime import timedelta


class ResCompany(models.Model):

    _inherit = 'res.company'


    @api.model
    def update_currency_rates(self):
        currency_changes = False
        last_updates = {x.id: x.l10n_ar_last_currency_sync_date for x in self.search([('currency_provider', '=', 'afip'),
            ('currency_interval_unit', '!=', False)])}

        super().update_currency_rates()
        for company in last_updates.keys():
            company_id = self.browse(company)
            if company_id.l10n_ar_last_currency_sync_date != last_updates[company]:
                currency_changes = True

        if currency_changes:
            self.env.ref(
                "product_replenishment_cost.ir_cron_update_cost_from_replenishment_cost"
            )._trigger(at=Datetime.now())
            # Este parametro lo agregamos para que sea modificable el tiempo entre crons
            time_difference = self.env['ir.config_parameter'].sudo().get_param("time_between_replenishment_costs","60")
            self.env.ref(
                "product_planned_price.ir_cron_update_price_from_planned"
            )._trigger(at=Datetime.now() + timedelta(minutes=int(time_difference)))
