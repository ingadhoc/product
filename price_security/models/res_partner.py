##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('property_product_pricelist')
    def check_property_product_pricelist(self):
        if self.user_has_groups('price_security.group_restrict_prices'):
            raise ValidationError(_(
                'You are not allowed to change the pricelist'))

    @api.constrains('property_payment_term_id')
    def check_property_payment_term_id(self):
        if self.user_has_groups('price_security.group_restrict_prices'):
            raise ValidationError(_(
                'You are not allowed to change the Payment Term'))
