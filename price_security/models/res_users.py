##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class Users(models.Model):
    _inherit = 'res.users'

    discount_restriction_ids = fields.One2many(
        'res.users.discount_restriction',
        'user_id',
        string='Discount Restrictions')

    @api.multi
    def check_discount(
            self, discount, pricelist_id,
            so_line=False, do_not_raise=False):
        """
        We add do_not_raise for compatibility with other modules
        """
        self.ensure_one()
        error = False

        # for compatibility with price_security
        pricelist = self.env['product.pricelist'].browse(pricelist_id)
        pricelist_disc = 0.0
        if so_line and 'discount_policy' in pricelist._fields and \
                pricelist.discount_policy == 'without_discount':
            tmp_line_vals = {
                'product_id': so_line.product_id.id,
                'order_id': so_line.order_id.id,
                'product_uom': so_line.product_uom.id,
                'product_uom_qty': so_line.product_uom_qty,
            }
            # for compatibility with product_pack
            if 'pack_parent_line_id' in so_line._fields:
                tmp_line_vals['pack_parent_line_id'] = so_line\
                    .pack_parent_line_id.id
            tmp_line = so_line.new(tmp_line_vals)
            tmp_line._onchange_discount()
            pricelist_disc = tmp_line.discount
        net_discount = discount - pricelist_disc

        if net_discount and net_discount != 0.0:
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
                # if pricelist_disc then we have a soline and e product
                if pricelist_disc:
                    error += ' (%s%% for product "%s")' % (
                        pricelist_disc, so_line.product_id.name)
            else:
                if (
                        net_discount < disc_restriction.min_discount or
                        net_discount > disc_restriction.max_discount
                ):
                    error = _(
                        'The applied discount is not allowed. Discount must be'
                        'between %s and %s for pricelist "%s"') % (
                        disc_restriction.min_discount + pricelist_disc,
                        disc_restriction.max_discount + pricelist_disc,
                        pricelist.name)
                    # if pricelist_disc then we have a soline and e product
                    if pricelist_disc:
                        error += ' and product "%s"' % (
                            so_line.product_id.name)
        if not do_not_raise and error:
            raise UserError(error)
        return error
