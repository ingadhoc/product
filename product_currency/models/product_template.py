##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):

    _inherit = "product.template"

    force_currency_id = fields.Many2one(
        'res.currency',
        'Force Currency',
        help='Use this currency instead of the product company currency',
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )

    @api.depends(
        'force_currency_id',
        'company_id',
        'company_id.currency_id')
    def _compute_currency_id(self):
        super(ProductTemplate, self)._compute_currency_id()
        for rec in self.filtered('force_currency_id'):
            rec.currency_id = rec.force_currency_id
