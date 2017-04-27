# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_quantities(self):
        # TODO: possible use super()
        res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for product in self:
            if product.pack:
                pack_qty = [math.floor(p.product_id.qty_available / p.quantity or 1) for p in product.pack_line_ids]
                product.qty_available = min(pack_qty)
            else:
                product.qty_available = res[product.id]['qty_available']
                product.incoming_qty = res[product.id]['incoming_qty']
                product.outgoing_qty = res[product.id]['outgoing_qty']
                product.virtual_available = res[product.id]['virtual_available']

    qty_available = fields.Float(
        compute='_compute_quantities'
    )
    pack_line_ids = fields.One2many(
        'product.pack.line',
        'parent_product_id',
        'Pack Products',
        help='List of products that are part of this pack.'
    )
    used_pack_line_ids = fields.One2many(
        'product.pack.line',
        'product_id',
        'On Packs',
        help='List of packs where product is used.'
    )

    @api.one
    @api.constrains('pack_line_ids')
    def check_recursion(self):
        """
        Check recursion on packs
        """
        pack_lines = self.pack_line_ids
        while pack_lines:
            if self in pack_lines.mapped('product_id'):
                raise UserError(_(
                    'Error! You cannot create recursive packs.\n'
                    'Product id: %s') % self.id)
            pack_lines = pack_lines.mapped('product_id.pack_line_ids')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # TODO rename a pack_type
    pack_price_type = fields.Selection([
        ('components_price', 'Detailed - Components Prices'),
        ('totalice_price', 'Detailed - Totaliced Price'),
        ('fixed_price', 'Detailed - Fixed Price'),
        ('none_detailed_assited_price', 'None Detailed - Assisted Price'),
        ('none_detailed_totaliced_price', 'None Detailed - Totaliced Price'),
    ],
        'Pack Type',
        help="* Detailed - Components Prices: Detail lines with prices on "
        "sales order.\n"
        "* Detailed - Totaliced Price: Detail lines on sales order totalicing "
        "lines prices on pack (don't show component prices).\n"
        "* Detailed - Fixed Price: Detail lines on sales order and use product"
        " pack price (ignore line prices).\n"
        "* None Detailed - Assisted Price: Do not detail lines on sales "
        "order. Assist to get pack price using pack lines."
    )
    pack = fields.Boolean(
        'Pack?',
        help='Is a Product Pack?',
    )
    pack_line_ids = fields.One2many(
        related='product_variant_ids.pack_line_ids'
    )
    used_pack_line_ids = fields.One2many(
        related='product_variant_ids.used_pack_line_ids'
    )
    qty_available = fields.Float(compute='_compute_quantities')

    @api.constrains(
        'product_variant_ids', 'pack_price_type')
    def check_relations(self):
        """
        Check assited packs dont have packs a childs
        """
        # check assited price has no packs child of them
        if self.pack_price_type == 'none_detailed_assited_price':
            child_packs = self.mapped(
                'pack_line_ids.product_id').filtered('pack')
            if child_packs:
                raise UserError(_(
                    'A "None Detailed - Assisted Price Pack" can not have a '
                    'pack as a child!'))

    @api.one
    @api.constrains('company_id', 'product_variant_ids')
    def check_pack_line_company(self):
        """
        Check packs are related to packs of same company
        """
        for line in self.pack_line_ids:
            if line.product_id.company_id != self.company_id:
                raise UserError(_(
                    'Pack lines products company must be the same as the '
                    'parent product company'))
        for line in self.used_pack_line_ids:
            if line.parent_product_id.company_id != self.company_id:
                raise UserError(_(
                    'Pack lines products company must be the same as the '
                    'parent product company'))

    @api.multi
    def write(self, vals):
        """
        We remove from prod.prod to avoid error
        """
        if vals.get('pack_line_ids', False):
            self.product_variant_ids.write(
                {'pack_line_ids': vals.pop('pack_line_ids')})
        return super(ProductTemplate, self).write(vals)

    @api.model
    def _price_get(self, products, ptype='list_price'):
        res = super(ProductTemplate, self)._price_get(
            products, ptype=ptype)
        for product in products:
            if (
                    product.pack and
                    product.pack_price_type in [
                        'totalice_price',
                        'none_detailed_assited_price',
                        'none_detailed_totaliced_price']):
                pack_price = 0.0
                for pack_line in product.pack_line_ids:
                    product_line_price = pack_line.product_id.price_get()[
                        pack_line.product_id.id] * (
                        1 - (pack_line.discount or 0.0) / 100.0)
                    pack_price += (product_line_price * pack_line.quantity)
                res[product.id] = pack_price
        return res

    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self:
            if template.pack:
                pack_qty = [math.floor(p.product_id.qty_available / p.quantity or 1) for p in template.pack_line_ids]
                template.qty_available = min(pack_qty)
            else:
                template.qty_available = res[template.id]['qty_available']
                template.virtual_available = res[template.id]['virtual_available']
                template.incoming_qty = res[template.id]['incoming_qty']
                template.outgoing_qty = res[template.id]['outgoing_qty']
