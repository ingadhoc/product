##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        one_variants = self.filtered('one_variant_per_product')
        for rec in one_variants:
            variant_alone = rec.attribute_line_ids.filtered(
                lambda r: len(r.value_ids) == 1).mapped(
                lambda t: t.value_ids[0])
            values = {'attribute_value_ids': [
                (6, 0, [x.id for x in variant_alone])]}\
                if rec.product_variant_ids else {
                'product_tmpl_id': rec.id,
                'attribute_value_ids': [
                    (6, 0, [x.id for x in variant_alone])]}
            rec.product_variant_ids.write(values) \
                if rec.product_variant_ids else \
                rec.product_variant_ids.create(values)
        return super(
            ProductTemplate, self - one_variants).create_variant_ids()

    @api.constrains('attribute_line_ids')
    def _check_one_variant_per_product(self):
        if self.one_variant_per_product:
            for variant_id in self.attribute_line_ids:
                if len(variant_id.value_ids) > 1:
                    raise ValidationError(_("Only 1 value for attribute."))

    @api.constrains('one_variant_per_product')
    def _check_variants(self):
        for rec in self.filtered('one_variant_per_product'):
            if len(rec.product_variant_ids) > 1:
                raise ValidationError(_(
                    'To set "One variant per product" product must have '
                    'only one variant. Deactivate/delete some variants or '
                    'remove some attributes to achieve that.'))
