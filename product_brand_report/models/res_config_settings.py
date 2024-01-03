##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_brand_invoice_report = fields.Boolean(
        "Show product brand on invoices",
        config_parameter='product_brand_report.show_brand_invoice_report'
    )
    show_brand_sales_report = fields.Boolean(
        "Show product brand on quotations & sale orders",
        config_parameter='product_brand_report.show_brand_sales_report'
    )
