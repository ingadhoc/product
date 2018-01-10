# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math


class ProductProduct(models.Model):
    _inherit = 'product.product'

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

    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_quantities(self):
        packs = self.filtered('pack')
        no_packs = (self + packs.mapped('pack_line_ids.product_id')) - packs
        res = super(ProductProduct, no_packs)._compute_quantities()
        for product in packs:
            pack_qty_available = []
            pack_virtual_available = []
            for subproduct in product.pack_line_ids:
                subproduct_stock = res[subproduct.product_id.id]
                sub_qty = subproduct.quantity
                if sub_qty:
                    pack_qty_available.append(math.floor(
                        subproduct_stock['qty_available'] / sub_qty))
                    pack_virtual_available.append(math.floor(
                        subproduct_stock['virtual_available'] / sub_qty))
            # TODO calcular correctamente pack virtual available para negativos
            res[product.id] = {
                'qty_available': (
                    pack_qty_available and min(pack_qty_available) or False),
                'incoming_qty': 0,
                'outgoing_qty': 0,
                'virtual_available': (
                    pack_virtual_available and
                    max(min(pack_virtual_available), 0) or False),
            }
        return res

    @api.multi
    @api.constrains('pack_line_ids')
    def check_recursion(self):
        """
        Check recursion on packs
        """
        for rec in self:
            pack_lines = rec.pack_line_ids
            while pack_lines:
                if rec in pack_lines.mapped('product_id'):
                    raise UserError(_(
                        'Error! You cannot create recursive packs.\n'
                        'Product id: %s') % rec.id)
                pack_lines = pack_lines.mapped('product_id.pack_line_ids')

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False,
                      company=False):
        packs = self.filtered(lambda p: p.pack and p.pack_price_type in [
            'totalice_price',
            'none_detailed_assited_price',
            'none_detailed_totaliced_price',
        ])
        no_packs = (self | self.mapped('pack_line_ids.product_id')) - packs
        prices = super(ProductProduct, no_packs).price_compute(
            price_type, uom, currency, company)
        for product in packs:
            pack_price = 0.0
            for pack_line in product.pack_line_ids:
                product_line_price = prices[
                    pack_line.product_id.id] * (
                    1 - (pack_line.discount or 0.0) / 100.0)
                pack_price += (product_line_price * pack_line.quantity)
            prices[product.id] = pack_price
        return prices


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

    @api.multi
    @api.constrains(
        'product_variant_ids', 'pack_price_type')
    def check_relations(self):
        """
        Check assited packs dont have packs a childs
        """
        # check assited price has no packs child of them
        for rec in self:
            if rec.pack_price_type == 'none_detailed_assited_price':
                child_packs = rec.mapped(
                    'pack_line_ids.product_id').filtered('pack')
                if child_packs:
                    raise UserError(_(
                        'A "None Detailed - Assisted Price Pack" can not have '
                        'a pack as a child!'))

        # TODO we also should check this
        # check if we are configuring a pack for a product that is partof a
        # assited pack
        # if self.pack:
        #     for product in self.product_variant_ids
        #     parent_assited_packs = self.env['product.pack.line'].search([
        #         ('product_id', '=', self.id),
        #         ('parent_product_id.pack_price_type', '=',
        #             'none_detailed_assited_price'),
        #         ])
        #     print 'parent_assited_packs', parent_assited_packs
        #     if parent_assited_packs:
        #         raise Warning(_(
        #             'You can not set this product as pack because it is part'
        #             ' of a "None Detailed - Assisted Price Pack"'))

    @api.multi
    @api.constrains('company_id', 'product_variant_ids')
    def check_pack_line_company(self):
        """
        Check packs are related to packs of same company
        """
        for rec in self:
            for line in rec.pack_line_ids:
                if line.product_id.company_id != rec.company_id:
                    raise UserError(_(
                        'Pack lines products company must be the same as the '
                        'parent product company'))
            for line in rec.used_pack_line_ids:
                if line.parent_product_id.company_id != rec.company_id:
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
