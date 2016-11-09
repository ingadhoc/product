# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    abc_sales_quantity = fields.Char(string='ABC Sales quantity')
    abc_sales_amount = fields.Char(string='ABC Sales amount')
    abc_sales_combined = fields.Char(
        compute='_get_abc_total',
        string='ABC Sales combined')

    @api.one
    def _get_abc_total(self):
        if self.abc_sales_quantity and self.abc_sales_amount:
            self.abc_sales_combined = \
                self.abc_sales_quantity + self.abc_sales_amount
        elif self.abc_sales_quantity and not self.abc_sales_amount:
            self.abc_sales_combined = self.abc_sales_quantity
        elif self.abc_sales_amount and not self.abc_sales_quantity:
            self.abc_sales_combined = self.abc_sales_amount
