# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product No Translation module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    description_sale = fields.Text(translate=False)
    description_purchase = fields.Text(translate=False)
    description = fields.Text(translate=False)
    name = fields.Char(translate=False)


class ProductCategory(models.Model):
    _inherit = "product.category"

    name = fields.Char(translate=False)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    name = fields.Char(translate=False)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    name = fields.Char(translate=False)


class ProductUomCateg(models.Model):
    _inherit = 'product.uom.categ'

    name = fields.Char(translate=False)


class ProductUom(models.Model):
    _inherit = 'product.uom'

    name = fields.Char(translate=False)
