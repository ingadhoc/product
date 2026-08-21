##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models

from .price_security_utils import hide_cost_fields

# inventory valuation fields added by stock_account on the lot form
COST_FIELDS = ("total_value", "avg_cost", "standard_price")


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        """The view is modified for price security users, so it can not be
        shared with the rest of the users
        """
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + (self.env.user.has_group("price_security.group_only_view_sale_price"),)

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if self.env.user.has_group("price_security.group_only_view_sale_price"):
            hide_cost_fields(arch, view_type, COST_FIELDS)
        return arch, view
