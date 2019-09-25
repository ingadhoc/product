##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    parent_id = fields.Many2one(
        ondelete='restrict',
    )
    parent_path = fields.Char(
        'Left',
        index=True,
    )
    complete_name = fields.Char(
        'Complete Name',
        related='display_name',
        readonly=True,
    )

    @api.constrains('sequence')
    def update_parents(self):
        # parent recompute is only trigger if parent_id field change
        # we force recompute also if we change sequence
        self._parent_store_compute()
