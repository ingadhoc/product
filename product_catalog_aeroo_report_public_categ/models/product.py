# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    # TODO. remove this: we dont use this order as default because it breaks
    # a litle spected order on website
    _order = 'parent_left, sequence, name'
    parent_id = fields.Many2one(ondelete='restrict')
    parent_left = fields.Integer('Left Parent', select=1)
    parent_right = fields.Integer('Right Parent', select=1)

    @api.constrains('sequence')
    def update_parents(self):
        # parent recompute is only trigger if parent_id field change
        # we force recompute also if we change sequence
        self._parent_store_compute()
