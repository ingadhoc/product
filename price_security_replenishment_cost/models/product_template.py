from odoo import models, api
import json


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            if self.env.user.has_group('price_security.group_only_view'):
                readonly_fields = (arch.xpath("//field[@name='replenishment_cost_type']")
                                    + arch.xpath("//field[@name='replenishment_cost_last_update']")
                                    + arch.xpath("//field[@name='replenishment_base_cost']")
                                    + arch.xpath("//field[@name='replenishment_base_cost_currency_id']")
                                    + arch.xpath("//field[@name='replenishment_cost']")
                                    + arch.xpath("//field[@name='replenishment_cost_rule_id']"))
                for node in readonly_fields:
                    node.set('readonly', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.env.user.has_group('price_security.group_only_view_sale_price'):
                invisible_fields = (arch.xpath("//group[@name='costing']"))
                for node in invisible_fields:
                    node.set('invisible', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
