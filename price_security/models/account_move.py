from odoo import models, api
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

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
        if view_type == 'form':
            if self.env.user.has_group('price_security.group_only_view'):
                fields = (arch.xpath("//field[@name='invoice_line_ids']/tree//field[@name='price_unit']")
                            + arch.xpath("//field[@name='invoice_line_ids']/tree//field[@name='tax_ids']"))
                for node in fields:
                    node.set('readonly', "parent.move_type in ('out_invoice', 'out_refund') and product_can_modify_prices == False")
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['readonly'] = "parent.move_type in ('out_invoice', 'out_refund') and product_can_modify_prices == False"
                    node.set("modifiers", json.dumps(modifiers))
                    node.set('force_save', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['force_save'] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
