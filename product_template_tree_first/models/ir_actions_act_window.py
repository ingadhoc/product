from odoo import api, models


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    @api.depends("view_ids.view_mode", "view_mode", "view_id.type")
    def _compute_views(self):
        """Force the list view to always be the first one, no matter what is
        configured in the action
        """
        super()._compute_views()
        product_template = self.sudo().filtered(lambda x: x.res_model == "product.template" and "list" in x.view_mode)
        for act in product_template.with_context(from_config=True):
            modes = act.view_mode.split(",")
            modes.remove("list")
            view_mode = ",".join(["list"] + modes)
            # assigning a stored field writes and clears the ormcache, even with the same value
            if act.view_mode != view_mode:
                act.view_mode = view_mode
            # views is a Json field: reading it returns a copy
            views = act.views
            for item in views:
                if item[1] == "list":
                    views.remove(item)
                    act.views = [item] + views
                    break
