##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import json

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("payment_term_id", "partner_id")
    def check_allowed_payment_term(self):
        for order in self:
            if not self.env.user.has_group("price_security.group_only_view"):
                continue

            partner_payment_term = order.partner_id.property_payment_term_id
            if not partner_payment_term or not order.payment_term_id:
                continue

            allowed = partner_payment_term.payment_term_allowed_ids

            if order.payment_term_id not in allowed and order.payment_term_id != partner_payment_term:
                raise UserError(
                    _("You are not allowed to select this payment term according to the restrictions configured")
                )

    @api.constrains("pricelist_id", "partner_id")
    def check_allowed_pricelist(self):
        for order in self:
            if not self.env.user.has_group("price_security.group_only_view"):
                continue

            partner_pricelist = order.partner_id.property_product_pricelist
            if not partner_pricelist or not order.pricelist_id:
                continue

            allowed = partner_pricelist.pricelist_allowed_ids

            if order.pricelist_id not in allowed and order.pricelist_id != partner_pricelist:
                raise UserError(
                    _("You are not allowed to select this pricelist according to the restrictions configured")
                )

    @api.onchange("partner_id")
    def check_partner_pricelist_change(self):
        if not self.env.user.has_group("product.group_product_pricelist"):
            return
        pricelist = self.partner_id.property_product_pricelist
        if self.order_line and pricelist != self._origin.pricelist_id:
            if self.env.user.has_group("price_security.group_only_view"):
                self.partner_id = self._origin.partner_id
                msj = _("You can not change partner if there are sale lines and pricelist is going to be changed")
            else:
                msj = _(
                    "The change of the customer generates a  change in the"
                    " price list, remember to check / update the prices"
                )
            return {"warning": {"title": "Warning", "message": msj}}

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        """The override of fields_get making fields readonly for price security users
        makes the view cache dependent on the fact the user has the group price security or not
        """
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return (
            key
            + (self.env.user.has_group("price_security.group_only_view"),)
            + (self.env.user.has_group("price_security.group_only_view_sale_price"),)
        )

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            if self.env.user.has_group("price_security.group_only_view"):
                fields = (
                    arch.xpath("//field[@name='order_line']/list//field[@name='price_unit']")
                    + arch.xpath("//field[@name='order_line']/list//field[@name='tax_id']")
                    + arch.xpath("//field[@name='order_line']/form//field[@name='price_unit']")
                    + arch.xpath("//field[@name='order_line']/form//field[@name='tax_id']")
                )
                for node in fields:
                    node.set("readonly", "product_can_modify_prices == False")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers["readonly"] = "product_can_modify_prices == False"
                    node.set("modifiers", json.dumps(modifiers))
                    node.set("force_save", "1")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers["force_save"] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
