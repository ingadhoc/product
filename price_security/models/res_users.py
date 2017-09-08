# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class DiscountRestriction(models.Model):
    _name = 'res.users.discount_restriction'
    _description = 'Discount Restriction'

    pricelist_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        ondelete='cascade',)
    min_discount = fields.Float('Min. Discount', required=True)
    max_discount = fields.Float('Max. Discount', required=True)
    user_id = fields.Many2one(
        'res.users',
        'User',
        required=True,
        ondelete='cascade',
    )


class Users(models.Model):
    _inherit = 'res.users'

    discount_restriction_ids = fields.One2many(
        'res.users.discount_restriction',
        'user_id',
        string='Discount Restrictions')

    @api.multi
    def check_discount(self, discount, pricelist_id, do_not_raise=False):
        """
        We add do_not_raise for compatibility with other modules
        """
        self.ensure_one()
        error = False
        if discount and discount != 0.0:
            disc_restriction_env = self.env['res.users.discount_restriction']
            domain = [
                ('pricelist_id', '=', pricelist_id), ('user_id', '=', self.id)]
            disc_restriction = disc_restriction_env.search(domain, limit=1)
            if not disc_restriction:
                domain = [
                    ('user_id', '=', self.id)]
                disc_restriction = disc_restriction_env.search(domain, limit=1)
            # User can not make any discount
            if not disc_restriction:
                error = _(
                    'You can not give any discount greater than pricelist '
                    'discounts')
            else:
                if (
                        discount < disc_restriction.min_discount or
                        discount > disc_restriction.max_discount
                ):
                    error = _(
                        'The applied discount is out of range with respect to '
                        'the allowed. The discount can be between %s and %s '
                        'for the current price list') % (
                        disc_restriction.min_discount,
                        disc_restriction.max_discount)
        if not do_not_raise and error:
            raise UserError(error)
        return error
