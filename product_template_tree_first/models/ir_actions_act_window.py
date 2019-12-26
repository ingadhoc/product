from odoo import api, models


class IrActionsActWindow(models.Model):

    _inherit = 'ir.actions.act_window'

    @api.depends('view_ids.view_mode', 'view_mode', 'view_id.type')
    def _compute_views(self):
        """ Force the tree view to always be the first one, no matter what is
        configured in the action
        """
        super()._compute_views()
        product_template = self.filtered(
            lambda x: x.res_model == 'product.template' and
            'tree' in x.view_mode)
        for act in product_template:
            modes = act.view_mode.split(',')
            modes.remove('tree')
            modes = ['tree'] + modes
            act.view_mode = ','.join(modes)
            for item in act.views:
                if item[1] == 'tree':
                    list_view = item
                    act.views.remove(item)
                    act.views = [list_view] + act.views
                    break
