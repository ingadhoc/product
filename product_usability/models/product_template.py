# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    active = fields.Boolean(track_visibility='onchange')
