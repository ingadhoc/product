##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
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
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_add_from_catalog(self):
        res = super().action_add_from_catalog()
        list_view_id = self.env.ref("product_catalog_tree.product_view_tree_catalog").id
        unique_views = {}
        for view_id, view_type in res.get("views", []):
            if view_type != "list" and view_type not in unique_views:
                unique_views[view_type] = (view_id, view_type)
        res["views"] = [(list_view_id, "list")] + list(unique_views.values())
        return res
