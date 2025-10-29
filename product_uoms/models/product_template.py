##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    uom_ids = fields.One2many(
        "product.uoms",
        "product_tmpl_id",
        copy=True,
        string="UOMs",
        help="Only uoms in this list will be available. "
        "If none is specified, then all uoms of product uom category will be "
        "available.",
    )

    @api.constrains("uom_ids", "uom_id")
    def _check_uoms(self):
        for rec in self:
            # Use _has_common_reference() to check if UoMs are compatible
            product_uom = rec.uom_id
            for uom_line in rec.uom_ids:
                if not product_uom._has_common_reference(uom_line.uom_id):
                    raise ValidationError(
                        _(
                            "UOMs must have the same reference unit as the Product Unit of Measure (%s)",
                            product_uom.name,
                        )
                    )
