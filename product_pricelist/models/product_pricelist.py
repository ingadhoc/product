##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from lxml import etree


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    price = fields.Monetary(
        compute='_compute_price',
        help='Price for product specified on the context',
    )
    show_products = fields.Boolean(
        'Show in products',
        default=True,
        help="By selecting it allows you to display the pricelist "
        "with the price of that product in the products",
    )

    def _compute_price(self):
        active_id = model = False
        if 'pricelist_product_id' in self._context:
            active_id = self._context.get('pricelist_product_id')
            model = 'product.product'
        elif 'pricelist_template_id' in self._context:
            active_id = self._context.get('pricelist_template_id')
            model = 'product.template'
        else:
            self.price = 0.0

        if active_id and model:
            for rec in self:
                rec.price = self.env[model].browse(active_id).with_context(pricelist=rec.id)._get_contextual_price()

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            if (self.env.user.has_group('sales_team.group_sale_salesman') or self.env.user.has_group('sales_team.group_sale_salesman_all_leads')) and not self.env.user.has_group('sales_team.group_sale_manager'):
                fields = (arch.xpath("//form"))
                for node in fields:
                    node.set('edit', "false")
        return arch, view
