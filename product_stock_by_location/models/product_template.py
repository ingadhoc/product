##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    location_ids = fields.One2many(
        "stock.location",
        compute="_compute_location_ids",
        string="Locations",
    )

    def _compute_location_ids(self):
        self.location_ids = self.env["stock.location"].search(
            [("show_stock_on_products", "=", True), ("usage", "=", "internal")]
        )

    def view_stock_detail(self):
        self.ensure_one()
        view = "product_stock_by_location.view_template_stock_by_location_form"
        return {
            "name": _("Stock By Locations"),
            "target": "new",
            "res_id": self.id,
            "view_mode": "form",
            "res_model": self._name,
            "view_id": self.env.ref(view).id,
            "type": "ir.actions.act_window",
        }
