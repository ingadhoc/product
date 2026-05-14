##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ProductUoms(models.Model):
    _inherit = "product.uoms"

    purchase_ok = fields.Boolean(
        default=True,
    )

    def unlink(self):
        purchase_order_line = self._get_blocking_purchase_order_line()
        if purchase_order_line:
            raise ValidationError(
                _(
                    "You cannot delete secondary unit of measure %(uom)s from %(product)s because it is used on purchase order %(order)s. Please update or remove the order line before deleting it.",
                    uom=purchase_order_line.product_uom.display_name,
                    product=purchase_order_line.product_id.display_name,
                    order=purchase_order_line.order_id.display_name,
                )
            )
        return super().unlink()

    def _get_blocking_purchase_order_line(self):
        pair_domains = [
            [("product_id.product_tmpl_id", "=", rec.product_tmpl_id.id), ("product_uom", "=", rec.uom_id.id)]
            for rec in self
        ]
        if not pair_domains:
            return self.env["purchase.order.line"]
        domain = expression.AND([expression.OR(pair_domains), [("state", "!=", "cancel")]])
        return self.env["purchase.order.line"].search(domain, limit=1)
