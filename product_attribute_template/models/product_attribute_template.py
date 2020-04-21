##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ProductAttributeTemplate(models.Model):
    _name = "product.attribute.template"
    _description = "product.attribute.template"

    name = fields.name = fields.Char(
        required=True
    )
    product_attribute_ids = fields.Many2many(
        'product.attribute',
    )
    product_tmpl_ids = fields.One2many(
        'product.template',
        'product_attribute_template_id',
    )
    product_qty = fields.Integer(
        '# Products', compute='_compute_products',
    )
    not_configured_product_qty = fields.Integer(
        '# Products Not Configured', compute='_compute_products',
    )
    line_ids = fields.Many2many(
        'product.template.attribute.line',
        compute='_compute_default_line_ids',
        inverse='_inverse_dummy_inverse',
    )

    def _compute_products(self):
        for rec in self:
            rec.product_qty = len(rec.product_tmpl_ids)
            rec.not_configured_product_qty = rec.product_tmpl_ids.search_count(
                [('attribute_line_ids.value_ids', '=', False),
                    ('id', 'in', rec.product_tmpl_ids.ids)])

    def update_attributes(self):
        self.ensure_one()
        for product_tmpl in self.with_context(non_create_values=True).product_tmpl_ids:
            for attribute in (
                    self.product_attribute_ids -
                    product_tmpl.attribute_line_ids.mapped('attribute_id')):
                product_tmpl.attribute_line_ids.create({
                    'attribute_id': attribute.id,
                    'product_tmpl_id': product_tmpl.id,
                })

    def _inverse_dummy_inverse(self):
        return True

    def _compute_default_line_ids(self):
        product_templates = self.product_tmpl_ids
        attributes = self.product_attribute_ids
        res = [
            (0, 0, {
                'product_tmpl_id': product_template.id,
                'attribute_id': attribute.id,
                'value_ids': False,
            })
            # if the product doesn't have an line for the attribute,
            # create a new one
            if not product_template.attribute_line_ids.filtered(
                lambda x: x.attribute_id == attribute) else
            # otherwise, return the line
            (4, product_template.attribute_line_ids.filtered(
                lambda x: x.attribute_id == attribute)[0].id)
            for product_template in product_templates
            for attribute in attributes
        ]
        self.line_ids = res
