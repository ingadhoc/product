from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderDiscount(models.TransientModel):
    _inherit = "sale.order.discount"

    discount_restriction = fields.Boolean(compute="_compute_discount_restriction")

    @api.depends("discount_type")
    def _compute_discount_restriction(self):
        restricted_types = {"amount", "so_discount"}
        user = self.env.user

        for wizard in self:
            if (
                wizard.discount_type in restricted_types
                and user.has_group("price_security.group_only_view")
                and wizard.sale_order_id.pricelist_id in user.discount_restriction_ids.mapped("pricelist_id")
            ):
                wizard.discount_restriction = True
            else:
                wizard.discount_restriction = False

    @api.constrains("discount_type")
    def _check_discount_type(self):
        if self.filtered("discount_restriction"):
            raise ValidationError(
                _("You do not have permission to apply this type of discount " "with the current pricelist.")
            )
