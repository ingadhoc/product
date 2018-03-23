# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from openerp import models, api, _
from openerp.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.one
    @api.constrains('product_tmpl_id', 'default_code', 'active')
    def check_unique_company_and_default_code(self):
        if self.active and self.default_code and self.company_id:
            filters = [('product_tmpl_id.company_id', '=', self.company_id.id),
                       ('default_code', '=', self.default_code),
                       ('active', '=', True)]
            prod_ids = self.search(filters)
            if len(prod_ids) > 1:
                raise UserError(_(
                    'There can not be two active products with the '
                    'same Reference code in the same company.'))

    @api.one
    @api.constrains('product_tmpl_id', 'barcode', 'active')
    def check_unique_company_and_barcode(self):
        if self.active and self.barcode and self.company_id:
            filters = [('product_tmpl_id.company_id', '=', self.company_id.id),
                       ('barcode', '=', self.barcode), ('active', '=', True)]
            prod_ids = self.search(filters)
            if len(prod_ids) > 1:
                raise UserError(_(
                    'There can not be two active products with the same '
                    'EAN code in the same company'))
