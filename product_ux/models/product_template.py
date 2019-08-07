##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    active = fields.Boolean(track_visibility='onchange')

    sellers_product_code = fields.Char(
        'Vendor Product Code',
        related='seller_ids.product_code',
    )

    warranty = fields.Float()
    user_company_currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_user_company_currency_id',
    )

    @api.depends()
    def _compute_user_company_currency_id(self):
        for rec in self:
            rec.user_company_currency_id = self.env.user.company_id.currency_id
