##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    group_kanban_prices_with_tax = fields.Boolean(
        "Prices with tax on products kanban view",
        implied_group='product_price_taxes_included.group_prices_with_tax',
    )
