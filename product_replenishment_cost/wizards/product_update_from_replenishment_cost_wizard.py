##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, models
from odoo.exceptions import UserError


class ProductUpdateFromReplenishmentCostWizard(models.TransientModel):
    _name = "product.update_from_replenishment_cost.wizard"
    _description = "Update product cost from replenishment cost"

    def confirm(self):
        self.ensure_one()
        active_ids = self.env.context.get("active_ids")
        active_model = self.env.context.get("active_model")
        if active_model != "product.template":
            raise UserError(_("Update from replenishment cost must be called from product " "template"))
        templates = self.env[active_model].browse(active_ids)
        # cursor en cero: la actualización manual no comparte el cursor del cron
        run = self.env["product.replenishment_cost.run"]._create_run(trigger="wizard", cursor_template_id=0)
        counters = templates._update_cost_from_replenishment_cost(run=run)
        run._finish()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "sticky": False,
                "title": self.env._("Replenishment cost update"),
                "message": self.env._(
                    "%(updated)s costs updated, %(unchanged)s without changes " "(%(templates)s products processed).",
                    updated=counters["updated_count"],
                    unchanged=counters["unchanged_count"],
                    templates=counters["template_count"],
                ),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
