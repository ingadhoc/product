##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    abc_sales_quantity = fields.Char(
        string='ABC Sales quantity',
        copy=False,
    )
    abc_sales_amount = fields.Char(
        string='ABC Sales amount',
        copy=False,
    )
    abc_sales_combined = fields.Char(
        compute='_compute_abc_total',
        string='ABC Sales combined',
    )

    @api.depends()
    def _compute_abc_total(self):
        for rec in self:
            if rec.abc_sales_quantity and rec.abc_sales_amount:
                rec.abc_sales_combined = \
                    rec.abc_sales_quantity + rec.abc_sales_amount
            elif rec.abc_sales_quantity and not rec.abc_sales_amount:
                rec.abc_sales_combined = rec.abc_sales_quantity
            elif rec.abc_sales_amount and not rec.abc_sales_quantity:
                rec.abc_sales_combined = rec.abc_sales_amount
