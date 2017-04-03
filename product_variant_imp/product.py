# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, SUPERUSER_ID, _
from openerp.exceptions import Warning


class product_attribute(models.Model):
    _inherit = "product.attribute"
    add_to_name = fields.Boolean('Add To Name?')


class product_product(models.Model):
    _inherit = 'product.product'

    @api.one
    @api.depends(
        'product_tmpl_id',
        'product_tmpl_id.name',
        'attribute_value_ids',
        'attribute_value_ids.attribute_id',
        'attribute_value_ids.attribute_id.add_to_name',
        'attribute_line_ids',
        'product_tmpl_id.attribute_line_ids.attribute_id.add_to_name',
        'product_tmpl_id.attribute_line_ids.value_ids',
        'product_tmpl_id.attribute_line_ids.value_ids.name',
    )
    def _get_complete_name(self):
        name = self.product_tmpl_id.name
        attributes_names = self.attribute_value_ids.filtered(
            lambda x: x.attribute_id.add_to_name).mapped('name')
        name = attributes_names and "%s (%s)" % (
            name, ", ".join(attributes_names)) or name
        self.name = name

    name = fields.Char(
        'Complete Name',
        compute='_get_complete_name',
        store=True,
    )

    @api.model
    def create(self, vals):
        if vals.get('name'):
            self = self.with_context(
                default_name=vals.get('name'))
        return super(product_product, self).create(vals)

# Overwrite of name_get function to avoid joining variants again
    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = context.get('display_default_code', True) and d.get(
                'default_code', False) or False
            if code:
                name = '[%s] %s' % (code, name)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(
                cr, user, partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
            # variant = ", ".join([v.name for v in product.attribute_value_ids])
            # name = variant and "%s (%s)" % (product.name, variant) or product.name
            name = product.name
            sellers = []
            if partner_ids:
                sellers = filter(
                    lambda x: x.name.id in partner_ids, product.seller_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and "%s" % (
                        s.product_name) or False
                    # seller_variant = s.product_name and "%s (%s)" % (
                    #     s.product_name, variant) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                    }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                }
                result.append(_name_get(mydict))
        return result


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    one_variant_per_product = fields.Boolean(
        help='Restrict so that only one variant per product can be created'
        ' (only one attribute value per attribute can be setted).'
        ' Also change odoo behaviour when changing attribute values:\n'
        '* False: default odoo behaviour, if you change an attribute or'
        ' remove it odoo creates a new variant.\n'
        '* True: change attributes wont change variants,'
        ' it will only update variants attributes')

    @api.multi
    def create_variant_ids(self):
        for tmpl_id in self:
            if tmpl_id.one_variant_per_product:
                variant_alone = []
                for variant_id in tmpl_id.attribute_line_ids:
                    if len(variant_id.value_ids) == 1:
                        variant_alone.append(variant_id.value_ids[0])
                tmpl_id.product_variant_ids.write(
                    {'attribute_value_ids': [
                        (6, 0, [x.id for x in variant_alone])]})
                return True
            else:
                return super(ProductTemplate, self).create_variant_ids()

    @api.one
    @api.constrains('attribute_line_ids')
    def _check_one_variant_per_product(self):
        if self.one_variant_per_product:
            for variant_id in self.attribute_line_ids:
                if len(variant_id.value_ids) > 1:
                    raise Warning(_("Only 1 value for attribute."))
