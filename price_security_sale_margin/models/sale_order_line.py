from odoo import models, api
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        """The override of fields_get making fields readonly for price security users
        makes the view cache dependent on the fact the user has the group price security or not
        """
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + (self.env.user.has_group('price_security.group_only_view'),) + \
            (self.env.user.has_group('price_security.group_only_view_sale_price'),)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'tree':
            if self.env.user.has_group('price_security.group_only_view'):
                readonly_fields = (arch.xpath("//field[@name='purchase_price']")
                                    + arch.xpath("//field[@name='margin']")
                                    + arch.xpath("//field[@name='margin_percent']"))
                for node in readonly_fields:
                    node.set('readonly', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.env.user.has_group('price_security.group_only_view_sale_price'):
                invisible_fields = (arch.xpath("//field[@name='purchase_price']")
                                    + arch.xpath("//field[@name='margin']")
                                    + arch.xpath("//field[@name='margin_percent']"))
                for node in invisible_fields:
                    node.set('column_invisible', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['column_invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
