##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import Warning


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
        for rec in self:
            if rec.one_variant_per_product:
                variant_alone = []
                for variant_id in rec.attribute_line_ids:
                    if len(variant_id.value_ids) == 1:
                        variant_alone.append(variant_id.value_ids[0])
                if rec.product_variant_ids:
                    rec.product_variant_ids.write(
                        {'attribute_value_ids': [
                            (6, 0, [x.id for x in variant_alone])]})
                else:
                    values = {
                        'product_tmpl_id': rec.id,
                        'attribute_value_ids': [
                            (6, 0, [x.id for x in variant_alone])]}
                    rec.product_variant_ids.create(values)
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

    @api.multi
    @api.constrains('one_variant_per_product')
    def _check_variants(self):
        for rec in self:
            if rec.one_variant_per_product:
                if len(rec.product_variant_ids) > 1:
                    raise Warning(_(
                        'To set "One variant per product" product must have '
                        'only one variant. Deactivate/delete some variants or '
                        'remove some attributes to achieve that.'))
