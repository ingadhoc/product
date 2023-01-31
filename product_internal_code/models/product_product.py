##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class ProductProduct(models.Model):

    _inherit = 'product.product'

    internal_code = fields.Char(
        'Internal Code', copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (not vals.get('internal_code', False) and not self.
                    _context.get('default_internal_code', False)):
                vals['internal_code'] = self.env[
                    'ir.sequence'].next_by_code('product.internal.code')
        return super().create(vals_list)

    _sql_constraints = {
        ('internal_code_uniq', 'unique(internal_code)',
            'Internal Code mast be unique!')
    }
