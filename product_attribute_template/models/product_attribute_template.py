##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, Command


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
    line_ids = fields.One2many(
        'product.template.attribute.line',
        inverse_name='product_attribute_template_id',
        compute='_compute_line_ids',
        store=True,
        readonly=False,
    )

    def _compute_products(self):
        for rec in self:
            rec.product_qty = len(rec.product_tmpl_ids)
            rec.not_configured_product_qty = rec.product_tmpl_ids.search_count([
                ('attribute_line_ids.value_ids', '=', False),
                ('id', 'in', rec.product_tmpl_ids.ids)
            ])

    def update_attributes(self):
        self.ensure_one()
        for product in self.product_tmpl_ids:
            for attr in (self.product_attribute_ids - product.attribute_line_ids.mapped('attribute_id')):
                product.attribute_line_ids.with_context(non_create_values=True).create({
                    'attribute_id': attr.id,
                    'product_tmpl_id': product.id,
                })

    @api.depends('product_attribute_ids')
    def _compute_line_ids(self):
        self.ensure_one()
        res = []
        for product in self.product_tmpl_ids._origin:
            for attr in self.product_attribute_ids._origin:
                res.append(Command.link(attr.id))
                attribute_line = product.attribute_line_ids.filtered(lambda x: x.attribute_id == attr)
                if not attribute_line:
                    self.env['product.template.attribute.line'].with_context(non_create_values=True).create({
                        'product_tmpl_id': product.id,
                        'attribute_id': attr.id,
                        'value_ids': False,
                        'product_attribute_template_id': self.id
                        })
        self.product_attribute_ids = res # Revisar por qué no quedan guardados los atributos
