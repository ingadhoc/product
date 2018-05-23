##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = "product.template"

    force_currency_id = fields.Many2one(
        'res.currency',
        'Force Currency',
        help='Use this currency instead of the product company currency'
    )

    @api.multi
    def _compute_currency_id(self):
        super(ProductTemplate, self)._compute_currency_id()
        for rec in self.filtered('force_currency_id'):
            rec.currency_id = rec.force_currency_id
