##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class ProductCatalogReport(models.Model):
    _name = 'product.product_catalog_report'
    _description = 'Product Catalog Report with Aeroo'

    name = fields.Char(
        required=True,
    )
    products_order = fields.Char(
        'Products Order Sintax',
        help='for eg. name desc',
        required=False,
    )
    categories_order = fields.Char(
        'Categories Order Sintax',
        help='for eg. name desc',
    )
    include_sub_categories = fields.Boolean(
        'Include Subcategories?',
    )
    only_with_stock = fields.Boolean(
        'Only With Stock Products?',
    )
    taxes_included = fields.Boolean(
        'Taxes Included?',
        help='Export prices with taxes included by default? This value will be'
        ' used as default on print catalog wizard',
    )
    print_product_uom = fields.Boolean(
        'Print Product UOM?',
    )
    product_type = fields.Selection(
        [('product.template', 'Product Template'),
         ('product.product', 'Product')],
        'Product Type',
        required=True,
    )
    prod_display_type = fields.Selection(
        [('prod_per_line', 'One Product Per Line'),
         ('prod_list', 'Product List'),
         ('variants', 'Variants'),
         ], 'Product Display Type',
    )
    report_id = fields.Many2one(
        'ir.actions.report',
        oldname='report_xml_id',
        string='Report',
        domain=[('report_type', '=', 'aeroo'),
                ('model', '=', 'product.product_catalog_report')],
        context={'default_report_type': 'aeroo',
                 'default_model': 'product.product'},
        required=True,
    )
    category_ids = fields.Many2many(
        'product.category',
        'product_catalog_report_categories',
        'product_catalog_report_id',
        'category_id',
        'Product Categories',
    )
    pricelist_ids = fields.Many2many(
        'product.pricelist',
        'product_catalog_report_pricelists',
        'product_catalog_report_id',
        'pricelist_id',
        'Pricelist',
    )

    category_type = fields.Selection(
        [('accounting_category', 'Accounting Category')],
        default='accounting_category',
        required=True,
    )

    @api.multi
    def prepare_report(self):
        context = dict(self._context.copy())
        categories = self.category_ids
        # because this value usually cames from wizard, if we call report from
        # this model, we add taxes_included parameter
        if 'taxes_included' not in context:
            context.update({'taxes_included': self.taxes_included})
        if self.include_sub_categories and categories:
            categories = self.env['product.category'].search(
                [('id', 'child_of', categories.ids)])
        context.update({
            'category_ids': categories.ids,
            'product_type': self.product_type,
            'pricelist_ids': self.pricelist_ids.ids,
            'products_order': self.products_order,
            'categories_order': self.categories_order,
            'only_with_stock': self.only_with_stock,
            'prod_display_type': self.prod_display_type,
            'print_product_uom': self.print_product_uom,
            'category_type': self.category_type,
        })
        return self.with_context(context)

    @api.multi
    def generate_report(self):
        """ Print the catalog
        """
        self.ensure_one()
        self = self.prepare_report()
        return self.report_id.report_action(self)
