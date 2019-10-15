##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields,  api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char(
        copy=False,
    )

    @api.constrains('product_tmpl_id', 'default_code', 'active')
    def check_unique_company_and_default_code(self):
        for rec in self:
            if rec.active and rec.default_code and rec.company_id:
                filters = [
                    ('product_tmpl_id.company_id', '=', rec.company_id.id),
                    ('default_code', '=', rec.default_code),
                    ('active', '=', True)]
                products = self.search(filters)
                if len(products) > 1:
                    raise ValidationError(_(
                        'There can not be two active products with the '
                        'same Reference code in the same company.'))
