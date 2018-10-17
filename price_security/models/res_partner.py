##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _inverse_product_pricelist(self):
        """ if user is in group restrict prices we still allow him to create
        partners without pricelist or to delete pricelist from partners"""
        if self.user_has_groups('price_security.group_restrict_prices') and \
                self.property_product_pricelist:
            raise ValidationError(_(
                'You are not allowed to change the pricelist'))
        return super(ResPartner, self)._inverse_product_pricelist()

    @api.constrains('property_payment_term_id')
    def check_property_payment_term_id(self):
        """ if user is in group restrict prices we still allow him to create
        partners without payment term or to delete payment term from
        partners"""
        if self.user_has_groups(
                'price_security.group_restrict_prices') and \
                self.filtered(lambda x: x.property_payment_term_id):
            raise ValidationError(_(
                'You are not allowed to change the Payment Term'))
